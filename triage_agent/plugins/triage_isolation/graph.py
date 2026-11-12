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
from diagnostic import IsolatedIncident

# ScaleGov catalog id. A local id like `gpt-5.6-sol` deploys, then 400s on chat.
MODEL = "gemini/gemini-4-argon"
MODEL_ID = MODEL
# Read-only set from triage_pod. Widen only with a reason: the deploy scan
# has no allowlist, and bash / websearch / webfetch each cost a deployment.
DISABLED = ('bash', 'read', 'write', 'edit', 'apply_patch', 'glob', 'grep', 'skill', 'websearch', 'webfetch')
MAX_CONTEXT_TOKENS = 200_000

BASE_PROMPT = "Local-only deterministic diagnostic."

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
    tools=coding_tools(WORKDIR, model_id=MODEL_ID, disabled=DISABLED),
    middleware=coding_middleware(
        WORKDIR, model_id=MODEL_ID, disabled=DISABLED, max_context_tokens=MAX_CONTEXT_TOKENS,
        extra=(IsolatedIncident(),)
    ),
    context_management=False,
    recall=False,
    # Public Harness events are required by AMS and the Slingshot renderer.
    output_schema=HarnessOutputSchema,
)
