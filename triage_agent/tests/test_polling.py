"""Deterministic collection fault injection; no live calls or model inference."""
import asyncio

from datetime import datetime, timezone
from email.utils import format_datetime
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "alert_triage"))
from stages import collect, submit, retry_after_seconds
from test_handoff import projection

try:
    import httpx
except ImportError:
    httpx = None


class Clock:
    def __init__(self):
        self.now, self.waits = 0.0, []
    def __call__(self): return self.now
    async def sleep(self, delay):
        self.waits.append(delay)
        self.now += delay


@unittest.skipIf(httpx is None, "httpx absent in plain CLI")
class PollingTests(unittest.TestCase):
    def setUp(self):
        self.ticket = {"invocation_id": "inv-child", "thread_id": "thread-child", "file_id": "fresh",
                       "sha256": "a" * 64, "attempts": 1, "platform_status": "submitted"}
        self.clock = Clock()
        self.calls = []

    def response(self, status=200, data=None, headers=None):
        return httpx.Response(status, json=data, headers=headers,
                              request=httpx.Request("GET", "https://managed/SECRET"))

    def run_collect(self, steps, *, timeout=90, ticket=None, recommendation=False):
        outer = self
        class Reader:
            async def get(self, url, *, timeout):
                outer.calls.append((url, timeout))
                assert 0 < timeout <= min(30, outer.limit - outer.clock.now)
                step = steps.pop(0)
                if isinstance(step, BaseException): raise step
                if callable(step): return await step()
                return step
        self.limit = timeout
        with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}), \
             patch("stages.remote_client", side_effect=AssertionError("no submission")), \
             patch("stages.submit", side_effect=AssertionError("no submission")):
            result = asyncio.run(collect(self.ticket if ticket is None else ticket, client=Reader(), timeout=timeout,
                                         recommendation=recommendation, clock=self.clock, sleep=self.clock.sleep))
        self.assertNotIn("SECRET", json.dumps(result))
        self.assertEqual(result.get("invocation_id"), (self.ticket if ticket is None else ticket).get("invocation_id"))
        return result

    def success(self):
        return [self.response(data={"status": "completed"}), self.response(data=projection(self.ticket))]

    def test_status_and_output_recovery(self):
        for error in (httpx.ConnectTimeout("SECRET"), httpx.ReadTimeout("SECRET"),
                      *[self.response(code, {"SECRET": "SECRET"}) for code in (429, 500, 502, 503, 504)]):
            with self.subTest(error=type(error).__name__):
                self.clock, self.calls = Clock(), []
                steps = self.success()
                result = self.run_collect([error, steps[0], httpx.ReadTimeout("SECRET"), steps[1]])
                self.assertEqual(result["application_status"], "partial")
                self.assertEqual(result["history_status"], "not_configured")
                self.assertEqual(len(result["exports"]), 1)
                self.assertEqual(self.clock.waits, [1, 2])
                self.assertEqual(result["polling_diagnostics"]["get_attempts"], 4)
                self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 2)
                self.assertEqual(result["polling_diagnostics"]["elapsed_seconds"], 3)
                self.assertEqual(result["attempts"], 1)  # submission count unchanged
                self.assertTrue(all(url.startswith("https://managed/v1/invocations/inv-child") for url, _ in self.calls))

    def test_retry_exhaustion_is_collection_wide_not_reset_by_success(self):
        result = self.run_collect([httpx.ReadTimeout("SECRET"), self.response(data={"status": "running"}),
                                   *[self.response(503) for _ in range(3)]])
        self.assertEqual(result["polling_diagnostics"]["stop_category"], "retry_exhausted")
        self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 3)
        self.assertEqual(self.clock.waits, [1, 2, 2, 4])
        self.assertEqual(len(self.calls), 5)
        self.assertEqual(result["error"], "collection_failed_uncertain")
        self.assertEqual(result["exports"], [])

    def test_deadline_backoff_poll_and_request_bounds(self):
        for steps, limit, calls in (([self.response(503)], .5, 1),
                                    ([self.response(data={"status": "running"})], 1, 1),
                                    ([], 0, 0)):
            self.clock, self.calls = Clock(), []
            result = self.run_collect(steps, timeout=limit)
            self.assertEqual(result["error"], "collection_timeout_uncertain")
            self.assertEqual(len(self.calls), calls)
            self.assertLessEqual(self.clock.now, limit)
        self.clock, self.calls = Clock(), []
        async def expire():
            self.clock.now += .5
            return self.response(data={"status": "completed"})
        result = self.run_collect([expire], timeout=.5)
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(result["polling_diagnostics"]["stop_category"], "deadline_exceeded")

    def test_real_async_deadline_cancels_hung_get(self):
        canceled = []
        class Reader:
            async def get(self, url, **kwargs):
                try: await asyncio.Event().wait()
                finally: canceled.append(True)
        with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
            result = asyncio.run(collect(self.ticket, client=Reader(), timeout=.01))
        self.assertEqual(result["error"], "collection_timeout_uncertain")
        self.assertEqual(canceled, [True])
        self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 0)

    def test_retry_after(self):
        for header, expected in (("5", [5]), ("-1", [1]), ("nan", [1]), ("SECRET", [1])):
            self.clock, self.calls = Clock(), []
            result = self.run_collect([self.response(429, headers={"Retry-After": header}), *self.success()])
            self.assertNotIn("error", result)
            self.assertEqual(self.clock.waits, expected)
        self.clock, self.calls = Clock(), []
        result = self.run_collect([self.response(503, headers={"Retry-After": "9999999999"})])
        self.assertEqual(result["polling_diagnostics"]["stop_category"], "retry_after_exceeds_bound")
        self.assertEqual(len(self.calls), 1)
        now = 1800000000
        self.assertEqual(retry_after_seconds(format_datetime(datetime.fromtimestamp(now + 7, timezone.utc)), now), 7)
        self.assertEqual(retry_after_seconds(format_datetime(datetime.fromtimestamp(now - 7, timezone.utc)), now), 0)
        for header in (None, "x" * 129, "inf", "1.5", "-1"):
            self.assertIsNone(retry_after_seconds(header, now))

    def test_permanent_failures_not_retried(self):
        for error in (*[self.response(code) for code in (400, 401, 403, 404, 409, 501, 505, 302)],
                      httpx.ConnectError("SECRET"), httpx.ReadError("SECRET"),
                      httpx.WriteTimeout("SECRET"), httpx.PoolTimeout("SECRET")):
            self.clock, self.calls = Clock(), []
            result = self.run_collect([error])
            self.assertEqual(result["error"], "collection_failed_uncertain")
            self.assertEqual(len(self.calls), 1)
            self.assertEqual(self.clock.waits, [])

    def test_invalid_ticket_data_receipts_and_schema_fail_closed(self):
        for ticket in ({}, {**self.ticket, "sha256": "bad"}, {**self.ticket, "invocation_id": "../other"},
                       {**self.ticket, "thread_id": None}):
            self.calls = []
            result = self.run_collect([], ticket=ticket)
            self.assertEqual(len(self.calls), 0)
            self.assertIn("ticket", result["error"])
        for data in ([], {}, {"status": "SECRET"}, {"status": []}):
            self.calls = []
            result = self.run_collect([self.response(data=data)])
            self.assertEqual(result["polling_diagnostics"]["stop_category"], "invalid_data_or_integrity")
            self.assertEqual(len(self.calls), 1)
        for bad in ([], {}, {"messages": [{"type": "tool", "name": "run_enrichment", "content": "bad"}]},
                    projection({**self.ticket, "sha256": "b" * 64})):
            self.calls = []
            result = self.run_collect([self.response(data={"status": "completed"}), self.response(data=bad)])
            self.assertEqual(result["exports"], [])
            self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 0)
            self.assertEqual(len(self.calls), 2)

    def test_output_204_and_terminal_failure(self):
        result = self.run_collect([self.response(data={"status": "completed"}), self.response(204), *self.success()])
        self.assertNotIn("error", result)
        self.assertEqual(self.clock.waits, [2])
        self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 0)
        for status in ("failed", "canceled", "interrupted", "requires_action"):
            self.calls = []
            result = self.run_collect([self.response(data={"status": status, "error_message": "SECRET"})])
            self.assertEqual(result["error"], "child_not_completed")
            self.assertEqual(len(self.calls), 1)

    def test_recommendation_output_recovery_and_count_integrity(self):
        from test_demo import DemoTests
        values = DemoTests().recommendation_projection()
        tool = values["messages"][0]
        data = json.loads(tool["content"])
        data.update(received_file_id=self.ticket["file_id"], source_sha256=self.ticket["sha256"])
        tool["content"] = json.dumps(data)
        result = self.run_collect([self.response(data={"status": "completed"}), self.response(502),
                                   self.response(data=values)], recommendation=True)
        self.assertEqual(result["counts"]["completed"], 7)
        self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 1)
        data["run"]["completed"] = 99
        tool["content"] = json.dumps(data)
        self.calls = []
        result = self.run_collect([self.response(data={"status": "completed"}), self.response(data=values)],
                                  recommendation=True)
        self.assertEqual(result["exports"], [])
        self.assertEqual(result["polling_diagnostics"]["stop_category"], "invalid_data_or_integrity")
        self.assertEqual(result["polling_diagnostics"]["retry_attempts"], 0)

    def test_failed_collection_keeps_upstream_artifacts_and_stops_routing(self):
        try:
            from file_first import file_first_message
            from langchain_core.messages import HumanMessage, ToolMessage
        except ImportError:
            self.skipTest("Agent Kit dependencies absent in plain CLI")
        from stages import current_results, stage_artifact
        upstream = {"run": {"accepted_findings": 1, "incident_groups": 1, "completed": 0, "failed": 1,
                             "errors": [], "status": "partial", "model": "none:deterministic-extraction"},
                    "indicator_export": {"status": "created", "file_id": "confirmed", "filename": "extracted_indicators.json"}}
        result = self.run_collect([self.response(401)])
        messages = [HumanMessage(content="investigate"),
                    ToolMessage(name="run_triage", tool_call_id="triage", content=json.dumps(upstream)),
                    ToolMessage(name="submit_enrichment", tool_call_id="submit", content=json.dumps(self.ticket)),
                    ToolMessage(name="collect_enrichment", tool_call_id="collect", content=json.dumps(result))]
        answer = file_first_message(messages)
        self.assertEqual(answer.tool_calls, [])
        self.assertIn("INVESTIGATION INCOMPLETE", answer.content)
        self.assertIn("previously confirmed attachments remain available", answer.content)
        self.assertEqual(stage_artifact("run_triage", current_results(messages)["run_triage"])["stage_exports"],
                         [upstream["indicator_export"]])

    def test_submit_once_then_recover_without_duplicate_submission(self):
        outer = self
        class Remote:
            last_invocation_id = None
            last_thread_id = None
            calls = 0
            async def astream(self, value, config):
                self.calls += 1
                self.last_invocation_id = outer.ticket["invocation_id"]
                self.last_thread_id = outer.ticket["thread_id"]
                yield {}
        remote = Remote()
        with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
            ticket = asyncio.run(submit(self.ticket, factory=lambda base: remote))
        result = self.run_collect([self.response(503), *self.success()], ticket=ticket)
        self.assertEqual(remote.calls, 1)
        self.assertNotIn("error", result)
        self.assertEqual(result["thread_id"], self.ticket["thread_id"])

    def test_cancellation_propagates(self):
        with self.assertRaises(asyncio.CancelledError):
            self.run_collect([asyncio.CancelledError()])
