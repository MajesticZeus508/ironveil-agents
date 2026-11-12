"""Exercise real Agent Kit wire models in the managed Python environment."""
import importlib.util
from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins" / "alert_triage"))
HAS_KIT = importlib.util.find_spec("spark_agent_kit") is not None


@unittest.skipUnless(HAS_KIT, "Run with Slingshot managed Python for Agent Kit contract checks")
class ProgressContractTests(unittest.TestCase):
    def test_remote_harness_marshalling_and_file_projection(self):
        import asyncio
        import httpx
        from handoff import remote_client, dispatch_input
        export = {"status": "created", "file_id": "fresh", "sha256": "hash"}
        from test_handoff import projection
        calls = []
        def respond(request):
            import json
            calls.append(request)
            if request.method == "POST":
                body = json.loads(request.content)
                self.assertEqual(body["input"], dispatch_input("fresh"))
                self.assertNotIn("thread_id", body)
                self.assertNotIn("authorization", request.headers)
                return httpx.Response(200, json={"thread_id": "thread", "invocation_id": "inv"})
            if request.url.path.endswith("/output"):
                return httpx.Response(200, json=projection(export))
            return httpx.Response(200, json={"id": "inv", "status": "completed"})
        remote = remote_client("https://managed")
        remote.async_transport = httpx.MockTransport(respond)
        values = asyncio.run(remote.ainvoke(dispatch_input("fresh"), config={"configurable": {}}))
        self.assertIn("messages", values)
        self.assertIn("render_events", values)
        self.assertEqual(sum(r.method == "POST" for r in calls), 1)
        from spark_agent_kit.api_contracts.harness.output.extensions import ToolOutcomeContext
        from file_output import IndicatorFileLifecycle
        blocks = IndicatorFileLifecycle().project_tool_outcome(ToolOutcomeContext(
            action_id="parent-call", tool_name="run_triage", artifact={
                "indicator_export": {**export, "filename": "extracted_indicators.json"},
                "enrichment_exports": [{"status": "created", "file_id": "child-json",
                                        "filename": "enrichment_results.json", "mime_type": "application/json"}],
                "recommendation_exports": [{"status": "created", "file_id": "report",
                                             "filename": "recommendation_report.md", "mime_type": "text/markdown"}]}))
        self.assertEqual([b.file_id for b in blocks], ["fresh", "child-json", "report"])

    def test_stream_and_durable_log_match_with_confirmed_file(self):
        from spark_agent_kit.api_contracts.harness.output.events import DeltaEvent, EventOrdinal
        from spark_agent_kit.api_contracts.harness.output.extensions import ToolOutcomeContext
        from file_output import IndicatorFileLifecycle
        from progress import TriageProgress
        events = []

        class Writer:
            def allocate_scoped_ordinals(self, index, scope):
                return EventOrdinal(step=1, path=scope, local=index), None

            def stream_only(self, event):
                events.append(DeltaEvent.model_validate(event.model_dump()))

        progress = TriageProgress("call-1", Writer())
        progress("Reading the uploaded findings…")
        progress("Reviewing incident group 1 of 1…")
        blocks = IndicatorFileLifecycle().project_tool_outcome(ToolOutcomeContext(
            action_id="call-1", tool_name="run_triage", artifact={
                "triage_progress": progress.artifact(),
                "indicator_export": {"status": "created", "file_id": "file-1", "filename": "extracted_indicators.json"}}))
        self.assertEqual(len(events), 2)
        self.assertEqual([e.event_id.local for e in events], [0, 1])
        self.assertTrue(all(e.payload.intent == "block_update" and e.action_id == "call-1" for e in events))
        self.assertEqual(blocks[0].text, "".join(e.payload.blocks[0].text for e in events))
        self.assertEqual(blocks[0].block_id, events[0].payload.blocks[0].block_id)
        self.assertEqual(blocks[0].type, "thinking")
        self.assertTrue(all(e.payload.blocks[0].type == "thinking" for e in events))
        self.assertEqual(blocks[0].text, "Reading the uploaded findings…\n\nReviewing incident group 1 of 1…\n\n")
        self.assertEqual(blocks[1].file_id, "file-1")

    def test_unavailable_stream_retains_log_without_claiming_file(self):
        from spark_agent_kit.api_contracts.harness.output.extensions import ToolOutcomeContext
        from file_output import IndicatorFileLifecycle
        from progress import TriageProgress
        from unittest.mock import Mock
        writer = Mock()
        writer.allocate_scoped_ordinals.side_effect = RuntimeError("No graph stream")
        progress = TriageProgress("call-2", writer)
        progress("Reading uploaded findings file.")
        progress("File creation failed or unconfirmed.")
        self.assertEqual(writer.allocate_scoped_ordinals.call_count, 1)
        blocks = IndicatorFileLifecycle().project_tool_outcome(ToolOutcomeContext(
            action_id="call-2", tool_name="run_triage", artifact={
                "triage_progress": progress.artifact(), "indicator_export": {"status": "failed"}}))
        self.assertEqual(len(blocks), 1)
        self.assertIn("File creation failed or unconfirmed", blocks[0].text)


if __name__ == "__main__":
    unittest.main()
