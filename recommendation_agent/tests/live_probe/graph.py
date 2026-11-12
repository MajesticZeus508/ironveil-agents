"""AMS entry point: a module-level `graph`.

The four names below are the substitution points — model, withheld tools,
context window, base prompt. Everything else is the pod contract:
`bundle_workdir`, the LiteLLM proxy, `with_billing`,
`context_management=False`, `recall=False`, and `graph = CompletionAgent(...)`.

`context_management=False` disables SAK auto-injection; `coding_middleware`
still supplies context management so the eviction buffer matches this
model's window.

`bundle_workdir` reads `$SLING_AGENT_WORKDIR` (the sandbox) when the runner
sets it; otherwise it resolves `workspace/` next to this file, where publish
places `fixture/`.
"""

import os
from pathlib import Path

from spark_agent_kit import CompletionAgent, ModelConfig
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema

from sling_agent.coding import coding_middleware, coding_prompt, coding_tools, with_billing
from sling_agent.coding.bundle import bundle_workdir
import json
import sys
from langchain.agents.middleware.types import AgentMiddleware, ModelResponse
from langchain_core.messages import AIMessage

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from ams.core import ArgonClient, parse, recommend, render_report


class Verify(AgentMiddleware):
    async def awrap_model_call(self, request, handler):
        import unittest
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_recommendation.py")
        import asyncio
        outcome = await asyncio.to_thread(unittest.TextTestRunner().run, suite)
        if not outcome.wasSuccessful():
            return ModelResponse(result=[AIMessage(content="Verification tests failed")])
        from ams.graph import graph as production_graph
        from uuid import uuid4
        missing = await production_graph.ainvoke({"task": {"intent": "dispatch", "payload": {"parts": [{"type": "text", "text": "Analyze"}]}}}, config={"configurable": {"thread_id": str(uuid4())}})
        print(json.dumps({"production_missing_file": str(missing)}, default=str), flush=True)
        results = []
        for name in ("verified_demo", "aws_pending"):
            path = ROOT.parent / "enrichment_agent" / "outputs" / name / "enrichment_results.json"
            data, digest = parse(path.read_bytes())
            result = await recommend(data, ArgonClient(), digest)
            print(json.dumps({"case": name, "run": result["run"], "analyses": [{"narrative": x["narrative"], "error": x["analysis_error"]} for x in result["incidents"]]}, allow_nan=False), flush=True)
            destination = ROOT / "outputs" / ("live_" + result["generated_at"].replace(":", "-") + "_" + name)
            destination.mkdir(parents=True, exist_ok=False)
            (destination / "recommendation_results.json").write_text(json.dumps(result, indent=2))
            (destination / "recommendation_report.md").write_text(render_report(result))
            results.append({"case": name, "run": result["run"], "report": render_report(result)})
        return ModelResponse(result=[AIMessage(content=json.dumps(results))])

# ScaleGov catalog id. A local id like `gpt-5.6-sol` deploys, then 400s on chat.
MODEL = "gemini/gemini-4-argon"
MODEL_ID = MODEL
# Read-only set from triage_pod. Widen only with a reason: the deploy scan
# has no allowlist, and bash / websearch / webfetch each cost a deployment.
DISABLED = ("apply_patch", "bash", "edit", "websearch", "webfetch", "write")
MAX_CONTEXT_TOKENS = 200_000

BASE_PROMPT = "Local-only verification runner. Never publish or use production attachments."

WORKDIR = bundle_workdir(Path(__file__).resolve().parent)

graph = CompletionAgent(
    model=ModelConfig(
        client="openai",
        model_name=MODEL,
        base_url=os.environ["LITELLM_PROXY_BASE_URL"],
        api_key=os.getenv("LITELLM_PROXY_API_KEY", "not-needed"),
        stream=True,
        client_kwargs=with_billing({}),
    ),
    system_prompt=coding_prompt(
        WORKDIR,
        model_id=MODEL_ID,
        disabled=DISABLED,
        base_prompt=BASE_PROMPT,
    ),
    tools=[],
    middleware=coding_middleware(
        WORKDIR, model_id=MODEL_ID, disabled=DISABLED, max_context_tokens=MAX_CONTEXT_TOKENS,
        extra=(Verify(),),
    ),
    context_management=False,
    recall=False,
    # Public Harness events are required by AMS and the Slingshot renderer.
    output_schema=HarnessOutputSchema,
)
