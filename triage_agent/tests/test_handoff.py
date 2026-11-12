import asyncio
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "alert_triage"))
from agent import StubClient
from hosted import analyze_uploaded, status_message
from handoff import dispatch_input, invoke_enrichment, verified_result


def projection(export):
    item = {"status": "created", "filename": "enrichment_results.json", "mime_type": "application/json", "file_id": "child-json"}
    result = {"run": {"status": "partial"}, "history_status": "not_configured",
              "handoff_receipt": {"file_id": export["file_id"], "sha256": export["sha256"], "schema": "alert-indicators/3"},
              "exports": [item], "export_status": "partial"}
    return {"messages": [{"type": "tool", "name": "run_enrichment", "tool_call_id": "child-call", "content": json.dumps(result)}],
            "render_events": [{"type": "OutcomeEvent", "action_id": "child-call", "payload": {"blocks": [
                {"type": "file", "file_id": "child-json"}]}}]}


class Store:
    def __init__(self, raw, failure=False):
        self.raw, self.failure, self.writes, self.reads = raw, failure, [], []
    async def read_file_bytes(self, file_id, max_bytes):
        self.reads.append(file_id)
        return SimpleNamespace(body=self.raw, status=200)
    async def write_file(self, filename, content, mime_type):
        self.writes.append(content)
        if self.failure:
            raise TimeoutError("SECRET")
        return SimpleNamespace(body={"id": f"fresh-{len(self.writes)}"}, status=200)


class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = (ROOT / "staging_input_verification.json").read_bytes()

    def test_exact_file_and_repeated_requests(self):
        store, calls = Store(self.raw), []
        async def child(export, **kwargs):
            calls.append(deepcopy(export))
            self.assertEqual(export["sha256"], hashlib.sha256(store.writes[-1].encode()).hexdigest())
            self.assertNotEqual(export["file_id"], "original-findings")
            return {"platform_status": "completed", **verified_result(projection(export), export)}
        for expected in ("fresh-1", "fresh-2"):
            output = asyncio.run(analyze_uploaded(["original-findings"], store, StubClient(), downstream=child))
            self.assertEqual(calls[-1]["file_id"], expected)
            self.assertEqual(output["downstream"]["application_status"], "partial")
            self.assertIn("not_configured", status_message(output))
        before = len(calls)
        output = asyncio.run(analyze_uploaded([], store, StubClient(), downstream=child))
        self.assertEqual(output["error"], "missing_upload")
        self.assertEqual(len(calls), before)
        self.assertEqual(store.reads, ["original-findings", "original-findings"])

    def test_invalid_empty_and_failed_export_do_not_dispatch(self):
        async def forbidden(*args, **kwargs):
            self.fail("must not invoke")
        for raw in (b"invalid", b"", b"\xff"):
            asyncio.run(analyze_uploaded(["current"], Store(raw), StubClient(), downstream=forbidden))
        store = Store(self.raw, failure=True)
        output = asyncio.run(analyze_uploaded(["current"], store, StubClient(), downstream=forbidden))
        self.assertEqual(output["indicator_export"]["status"], "failed")
        self.assertEqual(len(store.writes), 1)

    def test_partial_context_and_input_preserved_on_downstream_failure(self):
        class Broken:
            async def analyze(self, *args):
                raise TimeoutError("SECRET")
        async def child(export, **kwargs):
            raise TimeoutError("SECRET")
        store = Store(self.raw + b"\ninvalid")
        output = asyncio.run(analyze_uploaded(["current"], store, Broken(), downstream=child))
        self.assertEqual(output["run"]["status"], "partial")
        self.assertEqual(output["run"]["failed"], 7)
        self.assertEqual(output["indicator_export"]["status"], "created")
        self.assertEqual(len(json.loads(store.writes[0])["indicators"]), 98)
        self.assertNotIn("SECRET", json.dumps(output))

    def test_receipt_and_event_checks(self):
        export = {"file_id": "fresh", "sha256": "hash"}
        values = projection(export)
        self.assertEqual(len(verified_result(values, export)["exports"]), 1)
        with self.assertRaises(ValueError):
            verified_result(values, {**export, "file_id": "stale"})
        values["render_events"][0]["action_id"] = "old-call"
        self.assertEqual(verified_result(values, export)["exports"], [])

    def test_remote_timeout_failure_and_no_retry(self):
        export = {"status": "created", "file_id": "fresh", "sha256": "hash"}
        for mode in ("success", "failure", "timeout", "unacknowledged"):
            class Remote:
                last_thread_id = None
                last_invocation_id = None
                calls = 0
                async def ainvoke(self, value, config):
                    self.calls += 1
                    self.asserted_input = value
                    assert config == {"configurable": {}}
                    if mode == "unacknowledged":
                        raise TimeoutError("SECRET")
                    self.last_thread_id, self.last_invocation_id = "child-thread", "child-inv"
                    if mode == "timeout":
                        await asyncio.Event().wait()
                    if mode == "failure":
                        raise RuntimeError("SECRET")
                    return projection(export)
            remote = Remote()
            async def status(base, invocation):
                return "failed" if mode == "failure" else "running" if mode == "timeout" else "completed"
            with patch.dict("os.environ", {"AMS_API_URL": "https://managed"}):
                output = asyncio.run(invoke_enrichment(export, factory=lambda base: remote, status_reader=status, timeout=.02))
            self.assertEqual(remote.calls, 1)
            self.assertEqual(remote.asserted_input, dispatch_input("fresh"))
            self.assertNotIn("SECRET", json.dumps(output))
            self.assertEqual(output["platform_status"], {"success": "completed", "failure": "failed", "timeout": "running", "unacknowledged": "unknown"}[mode])
            if mode != "unacknowledged":
                self.assertEqual(output["invocation_id"], "child-inv")


if __name__ == "__main__":
    unittest.main()
