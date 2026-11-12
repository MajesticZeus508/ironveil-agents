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
import asyncio
import json
import sys
import unittest
from langchain.agents.middleware.types import AgentMiddleware, ModelResponse
from langchain_core.messages import AIMessage

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plugins"))


class Verify(AgentMiddleware):
    async def awrap_model_call(self, request, handler):
        from alert_triage.graph import graph as production
        from alert_triage import stages
        from unittest.mock import patch
        from langgraph.checkpoint.memory import InMemorySaver
        suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
        outcome = await asyncio.to_thread(unittest.TextTestRunner().run, suite)
        assert outcome.wasSuccessful(), "triage_tests_failed"
        recommendation_root = ROOT.parent / "recommendation_agent"
        suite2 = unittest.defaultTestLoader.discover(str(recommendation_root / "tests"), pattern="test_recommendation.py", top_level_dir=str(recommendation_root / "tests"))
        outcome2 = await asyncio.to_thread(unittest.TextTestRunner().run, suite2)
        assert outcome2.wasSuccessful(), "recommendation_tests_failed"
        async def extraction(*args, **kwargs):
            return {"run": {"accepted_findings": 1, "incident_groups": 1, "completed": 1, "failed": 0,
                            "errors": [], "status": "completed"},
                    "indicator_export": {"status": "created", "file_id": "triage", "filename": "extracted_indicators.json",
                                         "mime_type": "application/json", "sha256": "hash"}}
        async def submit(export, recommendation=False, **kwargs):
            return {"platform_status": "submitted", "application_status": "unknown", "exports": [],
                    "file_id": export["file_id"], "sha256": "hash", "invocation_id": "inv-test", "thread_id": "test-child"}
        async def collect(ticket, recommendation=False, **kwargs):
            prefix = "recommendation" if recommendation else "enrichment"
            return {**ticket, "platform_status": "completed", "application_status": "partial",
                    "counts": {"incident_count": 1, "completed": 1, "failed": 0},
                    "exports": [{"status": "created", "file_id": prefix + "-json", "filename": prefix + "_results.json", "mime_type": "application/json"},
                                {"status": "created", "file_id": prefix + "-report", "filename": prefix + "_report.md", "mime_type": "text/markdown"}]}
        async def prepare(child, store, invoke, **kwargs):
            return await invoke(child["exports"][0])
        from alert_triage import demo
        with patch.object(stages, "analyze_uploaded", extraction), patch.object(stages, "submit", submit), patch.object(stages, "collect", collect), patch.object(demo, "recommend_from_enrichment", prepare):
            production.compile(checkpointer=InMemorySaver())
            result = await production.ainvoke({"task": {"intent": "dispatch", "payload": {"parts": [{"type": "text", "text": "run"}]}}},
                                           config={"configurable": {"thread_id": "sdk-check"}})
            messages = result["messages"]
            assert "stages finished" in messages[-1].content, messages[-1].content
            assert len([m for m in messages if m.type == "tool"]) == 5
            files = [b for e in result["render_events"] if getattr(e, "type", None) == "OutcomeEvent"
                     for b in e.payload.blocks if b.type == "file"]
            assert len(files) == 5, "stage_files_missing"
        return ModelResponse(result=[AIMessage(content="SDK tests and five-stage checkpoint workflow passed")])

# ScaleGov catalog id. A local id like `gpt-5.6-sol` deploys, then 400s on chat.
MODEL = "gemini/gemini-4-argon"
MODEL_ID = MODEL
# Read-only set from triage_pod. Widen only with a reason: the deploy scan
# has no allowlist, and bash / websearch / webfetch each cost a deployment.
DISABLED = ("apply_patch", "bash", "edit", "websearch", "webfetch", "write")
MAX_CONTEXT_TOKENS = 200_000

BASE_PROMPT = "Local reliability verification."

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
        WORKDIR, model_id=MODEL_ID, disabled=DISABLED, max_context_tokens=MAX_CONTEXT_TOKENS, extra=(Verify(),)
    ),
    context_management=False,
    recall=False,
    # Public Harness events are required by AMS and the Slingshot renderer.
    output_schema=HarnessOutputSchema,
)
