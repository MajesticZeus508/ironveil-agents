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
from sling_agent.prompt_cache import PromptCacheMiddleware
if __package__:
    from .stages import make_stage_tools
    from .contracts import TriageInput, TriageOutput, TriageState
    from .file_output import indicator_file_output
    from .model_compat import provider_middleware
    from .persona import SOC_IDENTITY
    from .file_first import FileFirstMiddleware
else:
    from stages import make_stage_tools
    from contracts import TriageInput, TriageOutput, TriageState
    from file_output import indicator_file_output
    from model_compat import provider_middleware
    from persona import SOC_IDENTITY
    from file_first import FileFirstMiddleware

# ScaleGov catalog id. A local id like `gpt-5.6-sol` deploys, then 400s on chat.
MODEL = os.getenv("SPARK_MODEL_NAME", "gemini/gemini-4-argon")
MODEL_ID = MODEL
# Read-only set from triage_pod. Widen only with a reason: the deploy scan
# has no allowlist, and bash / websearch / webfetch each cost a deployment.
DISABLED = ('bash', 'websearch', 'webfetch', 'write', 'edit', 'apply_patch', 'skill', 'glob', 'grep', 'read')
MAX_CONTEXT_TOKENS = 200_000

WORKDIR = bundle_workdir(Path(__file__).resolve().parent)

# Routing and terminal text are supplied by code, not model inference. Keep the
# scaffold's model/billing/context construction for the hosted contract unchanged.
BASE_PROMPT = SOC_IDENTITY + "\nNetwork Investigation Demo. Process current original findings once through Triage, Historical Enrichment and Recommendation. Return verified report attachments and code-generated stage status. AWS history is unavailable, never simulated as live. No autonomous actions or outer generated chat summary."

graph = CompletionAgent(
    state_schema=TriageState,
    input_schema=TriageInput,
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
    tools=[*coding_tools(WORKDIR, model_id=MODEL_ID, disabled=DISABLED), *make_stage_tools(WORKDIR)],
    middleware=provider_middleware(coding_middleware(
        WORKDIR, model_id=MODEL_ID, disabled=DISABLED, max_context_tokens=MAX_CONTEXT_TOKENS,
        extra=(indicator_file_output(), FileFirstMiddleware())
    ), MODEL_ID, PromptCacheMiddleware),
    context_management=False,
    recall=False,
    # Public Harness events are required by AMS and the Slingshot renderer.
    output_schema=TriageOutput,
)
