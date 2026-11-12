import asyncio
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "alert_triage"))
from demo import recommend_from_enrichment
from handoff import invoke_enrichment, verified_result
from hosted import analyze_uploaded, status_message
from agent import StubClient


class DemoTests(unittest.TestCase):
    def child(self):
        receipt = {"file_id": "triage-export", "sha256": "triage-hash", "schema": "alert-indicators/3"}
        return {"platform_status": "completed", "application_status": "partial", "handoff_receipt": receipt,
                "file_id": "triage-export", "sha256": "triage-hash", "exports": [{"status": "created",
                "filename": "enrichment_results.json", "mime_type": "application/json", "file_id": "current-json"}]}

    def test_exact_json_hash_and_partial_allowed(self):
        child = self.child()
        raw = json.dumps({"schema": "alert-enrichment/1", "handoff_receipt": child["handoff_receipt"]}).encode()
        calls = []
        class Store:
            async def read_file_bytes(self, file_id, max_bytes):
                self_test.assertEqual(file_id, "current-json")
                return SimpleNamespace(status=200, body=raw)
        self_test = self
        async def invoke(export, **kwargs):
            calls.append(export)
            self.assertTrue(kwargs["recommendation"])
            self.assertEqual(export["sha256"], hashlib.sha256(raw).hexdigest())
            return {"platform_status": "completed", "application_status": "partial", "exports": []}
        output = asyncio.run(recommend_from_enrichment(child, Store(), invoke=invoke))
        self.assertEqual(output["application_status"], "partial")
        self.assertEqual(len(calls), 1)
        for bad in ({**child, "platform_status": "running"}, {**child, "exports": []},
                    {**child, "exports": child["exports"] * 2}, {**child, "sha256": "wrong"}):
            result = asyncio.run(recommend_from_enrichment(bad, Store(), invoke=invoke))
            self.assertEqual(result["platform_status"], "not_invoked")
        self.assertEqual(len(calls), 1)

    def recommendation_projection(self):
        result = {"run": {"status": "partial", "incident_count": 7, "completed": 7, "failed": 0},
                  "received_file_id": "current-json", "source_sha256": "digest", "export_status": "completed",
                  "exports": [{"status": "created", "filename": "recommendation_report.md",
                               "mime_type": "text/markdown", "file_id": "report"}]}
        return {"messages": [{"type": "tool", "name": "run_recommendation", "tool_call_id": "rec-call",
                              "content": json.dumps(result)}], "render_events": [{"type": "OutcomeEvent",
                "action_id": "rec-call", "payload": {"blocks": [{"type": "file", "file_id": "report"}]}}]}

    def test_recommendation_receipt_and_scoped_attachments(self):
        export = {"file_id": "current-json", "sha256": "digest"}
        values = self.recommendation_projection()
        result = verified_result(values, export, recommendation=True)
        self.assertEqual(result["counts"]["completed"], 7)
        self.assertEqual(len(result["exports"]), 1)
        with self.assertRaises(ValueError):
            verified_result(values, {**export, "sha256": "wrong"}, recommendation=True)
        values["render_events"][0]["action_id"] = "stale"
        self.assertEqual(verified_result(values, export, recommendation=True)["exports"], [])

    def test_recommendation_remote_once_and_timeout_uncertainty(self):
        export = {"status": "created", "file_id": "current-json", "sha256": "digest"}
        for hang in (False, True):
            outer = self
            class Remote:
                last_thread_id = "rec-thread"
                last_invocation_id = "rec-inv"
                calls = 0
                async def ainvoke(self, value, config):
                    self.calls += 1
                    assert config == {"configurable": {}}
                    assert value["task"]["payload"]["parts"][1]["resource"]["id"] == "current-json"
                    if hang:
                        await asyncio.Event().wait()
                    return outer.recommendation_projection()
            remote = Remote()
            async def status(*args):
                return "running" if hang else "completed"
            with patch.dict("os.environ", {"AMS_API_URL": "https://managed"}):
                result = asyncio.run(invoke_enrichment(export, recommendation=True, factory=lambda base: remote,
                                                      status_reader=status, timeout=.01))
            self.assertEqual(remote.calls, 1)
            self.assertEqual(result["invocation_id"], "rec-inv")
            self.assertEqual(result["platform_status"], "running" if hang else "completed")
            self.assertEqual(result["agent_id"], "2cf86942-3a14-40e4-95e5-4a90e752b259")

    def test_wrong_stage_input_no_export(self):
        class Store:
            async def read_file_bytes(self, *args, **kwargs):
                return SimpleNamespace(status=200, body=b'{"schema":"alert-indicators/3"}')
            async def write_file(self, *args, **kwargs):
                raise AssertionError("must not export")
        output = asyncio.run(analyze_uploaded(["wrong-input"], Store(), StubClient()))
        self.assertEqual(output["error"], "no_valid_findings")
        self.assertIn("original findings", status_message(output))

    def test_complete_sequence_status_and_current_export(self):
        raw = (Path(__file__).resolve().parents[1] / "staging_input_verification.json").read_bytes()
        order = []
        class Store:
            async def read_file_bytes(self, *args, **kwargs):
                return SimpleNamespace(status=200, body=raw)
            async def write_file(self, *args, **kwargs):
                return SimpleNamespace(status=200, body={"id": "fresh-triage"})
        async def enrich(export, **kwargs):
            order.append("enrichment")
            self.assertEqual(export["file_id"], "fresh-triage")
            return self.child()
        async def recommend(child, store, **kwargs):
            order.append("recommendation")
            self.assertEqual(child["handoff_receipt"], self.child()["handoff_receipt"])
            return {"platform_status": "completed", "application_status": "partial",
                    "counts": {"incident_count": 7, "completed": 7, "failed": 0},
                    "exports": [{"filename": "recommendation_report.md", "status": "created"}]}
        output = asyncio.run(analyze_uploaded(["original"], Store(), StubClient(), downstream=enrich,
                                             recommendation=recommend))
        self.assertEqual(order, ["enrichment", "recommendation"])
        text = status_message(output)
        self.assertIn("7/7 incident recommendations", text)
        self.assertIn("recommendation_report.md", text)
        self.assertIn("Human review required", text)
