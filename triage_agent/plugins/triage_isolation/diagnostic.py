"""Local-only diagnostic: reuse production prompt/client without editing it."""
import json
from pathlib import Path
import sys
import time

from langchain.agents.middleware.types import AgentMiddleware, ModelResponse
from langchain_core.messages import AIMessage

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "plugins" / "alert_triage"))
from agent import LiveContextClient, validate_context_response
from triage import parse_jsonl, group_findings, summarize


class IsolatedIncident(AgentMiddleware):
    async def awrap_model_call(self, request, handler):
        selection = request.state["messages"][-1].content
        target = "Nicollet Island" if "Nicollet" in selection else "197.43.113.112"
        records, info = parse_jsonl((PROJECT / "ueba_findings_sim_run2_2026-11-03.json").read_text())
        assert not info["errors"]
        group = next(g for g in group_findings(records) if g[0]["finding"]["entity"]["id"] == target)
        summary = summarize(group)
        client = LiveContextClient("gemini/gemini-4-argon")
        _, payload = client.prepare_request(group, summary, {})
        result = {"target": target, "model": client.model_name, "timeout_seconds": 90,
                  "findings": len(group), "observations": len(summary["indicators"]["observations"]),
                  "payload_bytes": len(json.dumps(payload).encode()), "retries": 0}
        started = time.monotonic()
        stage = "model_call"
        try:
            response = await client.analyze(group, summary)
            result["model_seconds"] = round(time.monotonic() - started, 3)
            stage = "response_validation"
            validated = validate_context_response(response, group, summary)
            result.update(status="completed", hypotheses=len(validated["possible_explanations"]),
                          checks=len(validated["recommended_next_steps"]))
        except Exception as exc:
            result.update(status="failed", stage=stage, error_type=type(exc).__name__)
        result["total_seconds"] = round(time.monotonic() - started, 3)
        print("ISOLATION_RESULT " + json.dumps(result), flush=True)
        return ModelResponse(result=[AIMessage(content=json.dumps(result))])
