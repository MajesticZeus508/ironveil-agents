"""Actual SDK/checkpointer chain with actual receivers, stubbed transport/model."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
sys.path.insert(0, str(ROOT / "plugins"))
HAS_KIT = importlib.util.find_spec("spark_agent_kit") is not None


@unittest.skipUnless(HAS_KIT, "Agent Kit required")
class ChainTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_receivers_checkpointed_chain_survives_intermediate_write_failures(self):
        import importlib
        from langgraph.checkpoint.memory import InMemorySaver
        from alert_triage import stages, handoff
        from enrichment_agent.ams.hosted import process_input as enrich
        from recommendation_agent.ams.hosted import process_input as report
        from recommendation_agent.ams.input_contract import RecommendationInput
        from enrichment_agent.ams.input_contract import EnrichmentInput

        class Store:
            def __init__(self, fail=False): self.writes, self.fail = [], fail
            async def read_file_bytes(self, *args, **kwargs):
                raise AssertionError("no intermediate file reads")
            async def write_file(self, filename, content, **kwargs):
                self.writes.append((filename, content))
                if self.fail: raise TimeoutError("PRIVATE")
                return SimpleNamespace(status=201, body={"id": "created-" + str(len(self.writes))})

        class Model:
            model_name, generation_method = "test_stub", "test_stub"
            async def analyze(self, packet):
                return {"summary": "TEST STUB: supplied observations require human review.",
                    "assessment": "Hypothesis: expected activity; identity and authorization need verification.",
                    "evidence": [{"claim": "Supplied observation retained.", "refs": ["O1"]}],
                    "recommendations": [{"action": "Verify the asset identity.", "rationale": "Identity is unresolved.",
                        "decision_if": "Escalate if independent evidence confirms unauthorized activity.",
                        "category": "investigate", "requires_approval": False, "refs": ["O1"]}] * 2,
                    "escalation_trigger": "Independent evidence confirms unauthorized activity.",
                    "limitations": ["TEST STUB; unavailable historical data."], "target_observation_ids": []}

        triage_store, enrichment_store, reporting_store = Store(True), Store(True), Store()
        submissions, outputs = [], {}
        tamper = False

        class Remote:
            last_thread_id = last_invocation_id = None
            def __init__(self, recommendation): self.recommendation = recommendation
            async def astream(self, value, config):
                self_test.assertEqual(config, {"configurable": {}})
                schema = RecommendationInput if self.recommendation else EnrichmentInput
                validated = schema.model_validate_json(json.dumps(value)).prepare_state_update()
                if self.recommendation:
                    result = await report(validated["source_file_ids"], validated["structured_enrichment"], reporting_store, Model())
                else:
                    result = await enrich(validated["source_file_ids"], validated["structured_handoff"], enrichment_store)
                    if tamper: result["structured_result"]["payload_sha256"] = "0" * 64
                index = len(submissions)
                self.last_thread_id, self.last_invocation_id = f"thread-{index}", f"inv-{index}"
                submissions.append(value)
                tool_name = "run_recommendation" if self.recommendation else "run_enrichment"
                outputs[self.last_invocation_id] = {"messages": [{"type": "tool", "name": tool_name,
                    "tool_call_id": f"call-{index}", "content": json.dumps(result)}], "render_events": [
                    {"type": "OutcomeEvent", "action_id": f"call-{index}", "payload": {"blocks": [
                        {"type": "file", "file_id": x["file_id"]} for x in result["exports"] if x["status"] == "created"]}}]}
                yield {}

        self_test = self
        def remote(base, agent_id, *args): return Remote(agent_id == stages.RECOMMENDATION_ID)
        class HTTP:
            async def __aenter__(self): return self
            async def __aexit__(self, *args): pass
            async def get(self, url, **kwargs):
                key = url.rstrip("/").split("/")[-2 if url.endswith("/output") else -1]
                value = outputs[key] if url.endswith("/output") else {"status": "completed"}
                return SimpleNamespace(status_code=200, json=lambda: value, raise_for_status=lambda: None)
        import httpx
        class RoutedHTTP(httpx.AsyncClient):
            async def get(self, url, **kwargs):
                if str(url).startswith("https://managed/"):
                    return await HTTP().get(url, **kwargs)
                raise AssertionError("unexpected network")

        event = json.loads((ROOT / "tests/fixtures/lux_staging_2026_11_13.json").read_bytes())
        def dispatch(e):
            return {"task": {"intent": "dispatch", "payload": {"parts": [
                {"type": "form", "slot": "lux_event", "params": {"event": e}}]}}}

        with patch.dict(os.environ, {"LITELLM_PROXY_BASE_URL": "http://127.0.0.1:4000", "AMS_API_URL": "https://managed"}), \
             patch("spark_agent_kit.SGPResourceClient", return_value=triage_store), \
             patch.object(stages, "remote_client", remote):
            module = importlib.import_module("alert_triage.graph")
            graph = importlib.reload(module).graph
            graph.compile(checkpointer=InMemorySaver())
            # Patch transport only after model construction: LangChain caches
            # HTTP wrappers across graph tests, and OpenAI checks concrete type.
            transport_patch = patch("httpx.AsyncClient.get", RoutedHTTP.get)
            transport_patch.start()
            self.addCleanup(transport_patch.stop)
            config = {"configurable": {"thread_id": "complete-structured-chain"}}
            result = await graph.ainvoke(dispatch(event), config=config)
            values = stages.current_results(result["messages"])
            self.assertEqual(len(values), 5, values)
            self.assertEqual(values["collect_recommendation"]["counts"]["completed"], 1)
            self.assertEqual(values["collect_recommendation"]["handoff_receipt"]["input_mode"], "structured")
            self.assertEqual(len(submissions), 2)
            self.assertEqual(len(triage_store.writes), 1)
            self.assertEqual(len(enrichment_store.writes), 1)
            saved = json.loads(reporting_store.writes[0][1])
            self.assertEqual(saved["actions_executed"], [])
            self.assertEqual(saved["upstream"]["history_source"]["status"], "not_configured")
            self.assertEqual(saved["run"]["status"], "partial")
            self.assertIsNone(saved["incidents"][0]["entity"]["id"])
            followup = await graph.ainvoke({"task": {"intent": "dispatch", "payload": {"parts": [
                {"type": "text", "text": "again"}]}}}, config=config)
            self.assertEqual(stages.current_results(followup["messages"])["run_triage"]["error"], "missing_upload")
            self.assertEqual(len(submissions), 2)
            tamper = True
            stopped = await graph.ainvoke(dispatch({**event, "finding_id": "fresh-second"}),
                config={"configurable": {"thread_id": "other-thread"}})
            values = stages.current_results(stopped["messages"])
            self.assertEqual(set(values), {"run_triage", "submit_enrichment", "collect_enrichment"})
            self.assertEqual(values["collect_enrichment"]["exports"], [])
            self.assertEqual(len(submissions), 3)
