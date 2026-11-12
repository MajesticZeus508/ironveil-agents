import asyncio
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "alert_triage"))
from stages import current_results, submit, stage_artifact, safe_error_class


class StageTests(unittest.TestCase):
    def test_extraction_only_keeps_exact_observations(self):
        from triage import analyze, ExtractionOnlyClient
        from agent import StubClient
        from export import build_indicator_export
        raw = (Path(__file__).resolve().parents[1] / "staging_input_verification.json").read_text()
        extracted = asyncio.run(analyze(raw, ExtractionOnlyClient()))
        baseline = asyncio.run(analyze(raw, StubClient()))
        a, b = build_indicator_export(extracted), build_indicator_export(baseline)
        self.assertEqual(a["indicators"], b["indicators"])
        self.assertEqual(a["extraction"], b["extraction"])
        self.assertTrue(all(i["analysis_error"]["code"] == "narrative_deferred" and i["context_status"] == "unavailable" for i in a["incidents"]))
        self.assertTrue(all(i["possible_explanations"] == [] for i in a["incidents"]))

    def test_turn_scoping_and_failure(self):
        human = SimpleNamespace(type="human")
        tool = lambda name, value: SimpleNamespace(type="tool", name=name, content=json.dumps(value), status="success")
        messages = [tool("collect_recommendation", {"old": True}), human,
                    tool("run_triage", {"indicator_export": {"status": "created", "file_id": "fresh"}})]
        self.assertEqual(set(current_results(messages)), {"run_triage"})
        self.assertEqual(stage_artifact("run_triage", current_results(messages)["run_triage"])["stage_exports"][0]["file_id"], "fresh")

    def test_submit_ticket_once_closes_observation_not_child(self):
        class Remote:
            last_invocation_id = None
            last_thread_id = None
            calls = 0
            closed = False
            async def astream(self, value, config):
                self.calls += 1
                assert config == {"configurable": {}}
                self.last_invocation_id, self.last_thread_id = "inv-child", "thread-child"
                try:
                    yield {"type": "ActionEvent"}
                    raise AssertionError("must not await entire child")
                finally:
                    self.closed = True
        remote = Remote()
        with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
            ticket = asyncio.run(submit({"file_id": "fresh", "sha256": "hash"}, factory=lambda base: remote))
        self.assertEqual(ticket["platform_status"], "submitted")
        self.assertEqual(ticket["invocation_id"], "inv-child")
        self.assertEqual(remote.calls, 1)
        self.assertTrue(remote.closed)

    def test_error_names_never_echo_provider_data(self):
        Secret = type("SECRET_PROVIDER_VALUE", (Exception,), {})
        self.assertEqual(safe_error_class(Secret("password")), "StageError")

    def test_read_only_collection_failure_preserves_ticket(self):
        try:
            import httpx
        except ImportError:
            self.skipTest("httpx absent in plain CLI")
        from stages import collect
        class Response:
            def raise_for_status(self): pass
            def json(self): return {"status": "failed", "failure_code": "GRAPH_EXECUTION_ERROR", "error_message": "SECRET"}
        class Reader:
            async def get(self, url, **kwargs): return Response()
        ticket = {"invocation_id": "inv-child", "thread_id": "thread-child", "file_id": "fresh", "sha256": "a" * 64}
        with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
            result = asyncio.run(collect(ticket, client=Reader()))
        self.assertEqual(result["invocation_id"], "inv-child")
        self.assertNotIn("SECRET", json.dumps(result))
