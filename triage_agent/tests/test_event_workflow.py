"""Real SDK/checkpointer graph; all resource and downstream calls are stubs."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins"))
HAS_KIT = importlib.util.find_spec("spark_agent_kit") is not None


@unittest.skipUnless(HAS_KIT, "Agent Kit required; run local reliability_verify probe")
class EventWorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def test_structured_event_stages_failure_and_thread_isolation(self):
        import importlib
        import alert_triage.graph as graph_module
        from alert_triage import stages, demo
        from langgraph.checkpoint.memory import InMemorySaver

        from test_event_ingestion import Store
        event = json.loads((ROOT / "tests/fixtures/lux_staging_2026_11_13.json").read_text())
        store = Store()
        calls = []
        failure = False

        async def submit(export, recommendation=False, **kwargs):
            calls.append("recommendation" if recommendation else "enrichment")
            if not recommendation:
                self.assertEqual(export["input_mode"], "structured")
                self.assertIsNone(export["file_id"])
                self.assertEqual(export["handoff"]["schema"], "alert-indicators/3")
            return {"platform_status": "submitted", "application_status": "unknown", "exports": [],
                    "file_id": export["file_id"], "sha256": "a" * 64,
                    "invocation_id": "inv-mock", "thread_id": "thread-mock"}

        async def collect(ticket, recommendation=False, **kwargs):
            if failure:
                return {**ticket, "error": "collection_timeout_uncertain", "exports": []}
            prefix = "recommendation" if recommendation else "enrichment"
            return {**ticket, "platform_status": "completed", "application_status": "partial",
                    "counts": {"incident_count": 1, "completed": 1, "failed": 0},
                    "exports": [{"status": "created", "file_id": prefix + suffix,
                        "filename": prefix + filename, "mime_type": mime}
                        for suffix, filename, mime in (("-json", "_results.json", "application/json"),
                                                      ("-report", "_report.md", "text/markdown"))]}

        async def prepare(child, store, invoke, **kwargs):
            return await invoke(child["exports"][0])

        def dispatch(value):
            return {"task": {"intent": "dispatch", "payload": {"parts": [
                {"type": "form", "slot": "lux_event", "params": {"event": value}}]}}}

        def tool_results(result):
            # Scope to latest invocation, never historical tools on reused threads.
            return stages.current_results(result["messages"])

        def files(result):
            return [b for e in result["render_events"] if getattr(e, "type", None) == "OutcomeEvent"
                    for b in e.payload.blocks if b.type == "file"]

        with patch("spark_agent_kit.SGPResourceClient", return_value=store), \
             patch.object(stages, "submit", submit), patch.object(stages, "collect", collect), \
             patch.object(demo, "recommend_from_enrichment", prepare), \
             patch.dict(os.environ, {"TRIAGE_EXTRACTION_ONLY": "true"}):
            # Tools capture the public resource client at construction time.
            # Rebuild application source under the stub; do not patch SDK internals.
            graph = importlib.reload(graph_module).graph
            graph.compile(checkpointer=InMemorySaver())
            config = {"configurable": {"thread_id": "lux-sdk-reused-thread"}}
            result = await graph.ainvoke(dispatch(event), config=config)
            tools = tool_results(result)
            self.assertEqual(len(tools), 5, {name: value.get("error") for name, value in tools.items()})
            self.assertEqual(calls, ["enrichment", "recommendation"])
            self.assertEqual(len(files(result)), 5)
            self.assertIn("stages finished", result["messages"][-1].content)
            receipt = tools["run_triage"]["run"]["event_receipt"]
            for name, value in tools.items():
                if name != "run_triage":
                    self.assertEqual(value["event_receipt"], receipt)
            self.assertEqual(len(store.writes), 1)
            self.assertEqual(store.writes[0]["extraction"]["accepted_findings"], 1)
            self.assertEqual(len(store.writes[0]["indicators"]), 7)
            self.assertEqual(store.writes[0]["incidents"][0]["entity"], event["entity"])
            self.assertTrue({"unknown_entity", "unknown_measure_semantics"} <= {
                q["kind"] for q in store.writes[0]["incidents"][0]["data_quality_issues"]})
            self.assertEqual(store.reads, [])

            # Reuse the actual checkpointed thread with text-only input: no stale event.
            empty = await graph.ainvoke({"task": {"intent": "dispatch", "payload": {"parts": [
                {"type": "text", "text": "run again"}]}}}, config=config)
            self.assertEqual(tool_results(empty)["run_triage"]["error"], "missing_upload")
            self.assertEqual(len(store.writes), 1)
            self.assertEqual(len(calls), 2)

            # A different event on the same thread gets its own receipt; an uncertain
            # Enrichment collection preserves triage but never submits Recommendation.
            changed = {**event, "finding_id": "second-synthetic-finding"}
            failure = True
            stopped = await graph.ainvoke(dispatch(changed), config=config)
            tools = tool_results(stopped)
            self.assertEqual(set(tools), {"run_triage", "submit_enrichment", "collect_enrichment"})
            new_receipt = tools["run_triage"]["run"]["event_receipt"]
            self.assertNotEqual(new_receipt["payload_sha256"], receipt["payload_sha256"])
            self.assertEqual(new_receipt["finding_ids"], ["second-synthetic-finding"])
            self.assertEqual(tools["collect_enrichment"]["event_receipt"], new_receipt)
            self.assertEqual(calls, ["enrichment", "recommendation", "enrichment"])
            self.assertEqual(len(store.writes), 2)
            self.assertIn("INVESTIGATION INCOMPLETE", stopped["messages"][-1].content)
