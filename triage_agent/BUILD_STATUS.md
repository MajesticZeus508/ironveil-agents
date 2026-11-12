# Build verification

## Current housekeeping checkpoint

Live AMS: entry **0.1.24**, Enrichment **0.1.3**, Recommendation **0.1.4**, all
active/latest. Fresh CLI Triage regression **60 discovered / 44 passed / 16 skipped**,
zero failures after test-only paths were corrected to the hash-verified
`staging_input_verification.json`. No deployed code or historical artifacts changed.
Prior managed verification passed 60 Triage + 15 Recommendation without skips.
Latest hosted evaluation: 28/35 analyses, five chains/five files each; see
[team evaluation](../EVALUATION.md). Local staging release and Dev working source
are separate; [inventory](../AMS_INVENTORY.md) records backup gaps.

## Historical checkpoint — 2026-11-10, before staging rebuild

0.1.23 active/latest, AMS automatic rebuild of 0.1.22, source
`b0562145-fe1e-4c14-b2e0-1c7dcc20272d`. Default extraction-only Triage and five
checkpoint-sized orchestration stages are deployed. Latest operator run
`inv_b394de1e-5e49-4616-8495-f936041f9844` completed in 206.181s with five
attachments and 7/7 recommendations. Prior managed regression passed 48 Triage
and 15 Recommendation tests without skips. Image remediation remains unverified.
See [current runbook](../DEMO.md). All entries below are historical checkpoints.

## Historical 0.1.17 housekeeping

This file is a historical verification ledger. Older statements of “latest”,
“pending”, “no downloads”, or “not implemented” describe their checkpoint, not
the current product. README.md is current usage; SESSION_HISTORY.md is the
chronological handoff. Operator subsequently confirmed the thinking presentation
works well in Donovan (not independent builder browser automation).

AMS now reports **0.1.17 active/latest**. Downloaded source uses the same bundle
file as 0.1.16 and all 14 files match the editable pod byte-for-byte. Snapshot:
ams_snapshots/0.1.17/alert_triage. See LOCAL_BACKUP.md for hashes and scope.
All 32 tests passed again during documentation cleanup. No code/deployment change
or new live inference run; original fixture preserved. The creation action for
0.1.17 is not established in the available session record.

## Thinking presentation — 0.1.16

32 tests pass, including real Agent Kit thinking-delta/durable-block validation,
paragraph spacing, unchanged 17/7/98 extraction, and explicit input/context errors.
No timestamp/repetitive completion messages or added inference calls. Builder check
ready=true, no blockers; local Semgrep unavailable. Managed probe imports but its
legacy messages input is rejected before inference by the required Harness schema
(existing probe limitation). Version 0.1.16 is active/latest in staging, agent
d4ffbfc9-696f-4a5a-b174-75daaa1c993f. Hosted fixture invocation
inv_0ed6c7bf-c868-4f73-b74b-44a15992c0f0, thread
390351f6-d42f-493d-97c7-e80124c1994a, completed. Stored output verified:
messages/render_events only, concise paragraph-separated thinking block without
timestamps, explicit context failures, final AI status and confirmed FileBlock
4d9933ea-0354-4022-a818-7572219adce6. 17 findings/seven groups/98 observations
exported; five contexts passed, two hit existing 90-second model timeouts. Run
correctly marked partial. About 287.65 seconds submission-to-completion.
Live SSE read was interrupted because the endpoint stays open; this run does
not independently verify live delivery or browser placement. No new invocation
was needed to finish verification. Fresh Donovan chat visual check remains.

## Execution updates — 0.1.15

31 tests pass with Slingshot managed Python, including real Agent Kit event
validation, streamed/durable log identity, and unavailable-stream/export-failure
handling. Existing extraction test still yields 17 findings/seven groups/98
observations. Stage/group callbacks add no model calls. Log bound covers all
100 possible groups. RuntimeError from missing stream context preserves the
final log. Agent Kit v0.50.0 writer/events/ToolOutcomeContext APIs were inspected.

Builder check: ready=true/no blockers; local Semgrep unavailable. The generic
CLI publish did not resolve this workspace pod and was blocked before upload;
the AMS builder's pod-specific packaging successfully submitted 0.1.15, source
bundle file 7244f390-7446-4715-b003-3f07ac53b6d3. Version 0.1.15 is active.

Hosted live-upload verification completed (UTC 2026-11-06): invocation
inv_dfd0e08f-d7fc-4924-bf7b-d74282d743ec, thread
727f29c5-e52a-4a6b-8a61-c0f3110616f8. HTTP 200 thread SSE delivered 19 progress
DeltaEvents while running, including each group's start/completion and file
creation. Concatenated fragments exactly match the 19-line durable tool log;
stored output contains that log and confirmed FileBlock. All 17 findings/seven
contexts/98 observations completed, zero context failures/input errors. File:
db737e2a-2613-46da-a032-1ca39dcf5440. Wall time 103.339s from submission,
97.065s after start; single-run result, not a latency guarantee. Evidence saved
in outputs/progress_verification_0.1.15.json.

No browser visual verification is claimed; reference Donovan supports
block_update text but drops numeric progress events. The remaining blocker is
access to a browser session running the deployed Donovan UI. See DONOVAN.md.

## Compact export — 0.1.14

28 tests pass. Version 3 preserves all selected values, stable indicator hashes,
reference occurrences, validated context text, existing summaries/recommendations,
and failure statuses. Detailed v2 helper retained; CLI --audit-export supported.
98 observations/seven incidents; local stub comparison 247043 -> 57345 bytes
(76.8% reduction). No model or parsing/validation change. Package ready=true,
no blockers; local Semgrep unavailable. Probe imports but cannot send Harness input.
Version 0.1.14 active/latest (0.1.13 already existed remotely). Hosted real-upload
test inv_f836b554-6e12-4380-bc69-f1907d12cd41, thread
a9f682c3-3903-4780-9338-60b46e5b955d running; final counts/file pending.

## Context reliability fixes — 0.1.12

Valid clock tokens excluded from IPv6 candidate scan; compressed/full IPv6 and
invented/malformed IPv4 remain checked. Context-only calls bind a strict JSON
schema (two keys, bounded arrays and 300-character strings). Local validation
still enforces length, explicit hypothesis labels and grounded indicators; no
silent truncation, retry, model fallback or timeout increase. Failure diagnostics
include stage/code/field and per-group elapsed seconds, in run.analysis_failures
and exported triage_context.analysis_error. 27 offline tests pass. Managed probe
imports but still cannot send Harness envelope. Package ready=true/no blockers;
local Semgrep unavailable. Version 0.1.12 active/latest. Hosted real-upload test
inv_8810bb70-a357-4757-a8dd-65774799f354, thread
d52b7f52-c0a1-4c07-b374-62e7aa534958, is running. First Argon call returned JSON
after 27.02s with schema-bound request; no gateway schema rejection. Full local
validation and final group/export counts: COMPLETED, 17 accepted findings, seven
groups, seven completed contexts, zero failures/input errors, analysis_failures=[].
98 observations exported, file 13ffb376-b001-4289-a7ab-83e4e9032aea. Durable FileBlock
and final AI status verified in stored output. Wall time 115.23s from creation,
109.01s after started_at (prior 0.1.11 benchmark 275.39s from creation with four
failures). This is a single successful comparison, not a guarantee against future
timeouts or schema deviations. 90s timeout and no retry remain unchanged.

## File-first experiment — 0.1.11

Deterministic model-call middleware bypasses outer provider calls, requesting
run_triage once and returning only code-generated status. Existing Harness tool
and FileBlock lifecycle is preserved. Context-only Argon calls request two short
lists with bounded lengths, use compact input without duplicated raw findings or
occurrence inventory, and reuse indicator/prose validation. Hosted Markdown and
full triage tool payload removed; CLI full-report path unchanged. No concurrency.

24 offline unittest checks pass. Pinned v0.50.0 completion.py, middleware/base.py
and agents/_create.py inspected for public wrap_model_call/ModelResponse behavior.
Managed probe imports successfully but rejects legacy messages before inference;
Harness required. builder_check ready=true, no blockers; local Semgrep absent.
Argon gateway streaming/system/tool-schema preflight passed. Version 0.1.11
is active/latest in ScaleGov staging. Missing-upload Harness smoke completed
(inv_ad94b48b-b38c-4488-91d9-7cb42175ae93), returning deterministic status.
Stored output contains only messages/render_events with paired tool/dispatch
events. Generate events still label deterministic model-node passes, but those
passes do not call the provider.

Real-upload test reused the authorized source file from the user's benchmark:
inv_b619dcf3-790a-4242-932a-a195c310a28c, thread
a2cf66cd-eed0-444d-bb85-57b86b4626c5. Completed in 275.39s from creation
(270.49s after started_at), versus 385.14s for the prior 0.1.10 run: about 29%
less wall time, single-run comparison only. Exactly seven ChatOpenAI spans
(267.83s total); deterministic outer model-node passes totaled 3.88ms.
17 findings/seven groups/98 observations exported, confirmed file metadata and
durable FileBlock: 81c52898-e177-46ea-93a1-a4b0119d2cf8 (247918 bytes).
IMPORTANT: only three context analyses passed; four failed. At least one failed
call hit the existing 90s request timeout (APITimeoutError), verified in its span.
Do not interpret shorter elapsed time as equivalent narrative success or claim
all seven contexts are present. Full failure attribution and a repeat benchmark
remain; no automatic retries, model fallback or weakened validation applied.
Actual file content/browser download not manually audited in this test.

## Incident-level context export — 0.1.10 publication

Updated extracted_indicators.json to alert-indicators/2. Export includes one
triage_context per incident group: validated hypotheses, recommended defensive
checks, limitations, narrative status, model provenance and explicit fallibility/
non-execution warnings. Each observation links by triage_context_id; identity
includes entity/window because incident_key alone can collide across groups.
Existing indicator ID computation and deterministic fields are unchanged.
Failed/invalid narratives produce unavailable context with empty narrative lists,
while extraction remains valid. No prompt, model, dependency or Agent Kit API
changes; no new integration or automated downstream invocation.

22 unittest checks pass, including exact narrative copy/provenance/linkage,
version-1 indicator identity compatibility, narrative-independent IDs, failed and
invalid narratives, partial/empty exports and shared incident keys. CLI stub run
regenerated outputs: 17 accepted findings, seven groups, 98 observations and seven
context entries. Original fixture hash unchanged. These are test-stub narratives,
not new live-model verification. builder_check ready=true, blockers=[]; security
scan unavailable because Semgrep is not installed. Publication of 0.1.10 accepted
in ScaleGov staging for agent d4ffbfc9-696f-4a5a-b174-75daaa1c993f; deployment
now active/latest. Gemini Argon streaming/system/tool-schema preflight
passed. Managed probe imported the graph but rejected its legacy messages input
before inference (the graph requires Harness task input); no gateway call was
made. Hosted Harness smoke invocation inv_fddfbf7d-b02a-42db-a9d5-90bdf79779df
(thread b639ffae-9d22-42c1-94b3-7f88f883508d) completed with a reply reporting
missing_upload and no fabricated export. This verifies deployed startup/chat,
not a real uploaded-file export; version-2 export content is covered by the
22 offline tests and CLI stub example. A real upload/download check remains.

## Defensive SOC prompt update — 0.1.9

Added shared SOC_IDENTITY to both chat BASE_PROMPT and incident PROMPT. Prompt-only
behavior change: calm defensive analyst voice with bounded extraction/handoff
mission. No parser, validator, export, model or tool changes. 18 tests pass.
builder_check ready=true, no blockers; local Semgrep unavailable. Managed probe
import succeeds but its messages envelope remains incompatible with Harness input.
Version 0.1.9 is active/latest. Hosted persona smoke test completed:
inv_adc5d17d-3708-4780-a040-6f8f8fb5e8f2, thread
56e588af-05c1-4b6d-8921-eec7a37e266c. Reply identifies itself as a SOC analyst,
names all nine fields and bounded defensive scope, and invents no findings.

## Gemini cache compatibility fix — 0.1.8

Inspected sling-agent-v0.1.0.dev6 factory/cache source. Confirmed factory adds
PromptCacheMiddleware and it sends prompt_cache_key to every ChatOpenAI proxy
request. Application now omits this optional middleware at construction for Gemini
only; no monkeypatch or dependency edit. Other middleware order preserved.
17 tests pass; builder_check ready=true, no blockers, local Semgrep unavailable.
Managed probe imports but legacy messages input cannot exercise Harness graph.
Version 0.1.8 is active/latest. Hosted invocation
inv_dca57164-ce96-414f-ab7e-05fcf25bce71, thread
5db3e2f1-5c0a-487b-9fab-63f7ba2ab501 selected Argon, successfully emitted a
run_triage tool call, and began successful per-group ChatOpenAI model calls.
Trace metadata no longer includes prompt_cache_key. Original HTTP 400 is resolved.
Full seven-group completion and export status are still pending at this checkpoint.
Separate hosted Argon tool-call + final-answer smoke test completed successfully:
inv_59d706ea-0c84-406d-a0ea-29aefd12c880, thread
1eac0796-14ec-4c95-99ff-f4d44f7eadba. Exactly one run_triage call, missing_upload
reported correctly, final AI reply returned; no model execution failure.

## Gemini Argon switch — 0.1.7

Both model defaults changed to gemini/gemini-4-argon. Catalog and streaming/system/
tool-schema compatibility check passed. Sixteen deterministic tests pass.
Managed probe imports but rejects its legacy messages input before inference;
use hosted Harness invocation to verify the actual request contract. Package
ready=true/no blockers; local Semgrep unavailable. Published 0.1.7; activation
and version 0.1.7 is active/latest. Hosted invocation
inv_654098d2-8681-4df8-9578-2293d94af672 (thread
dc770a9c-8779-4d6a-97f0-b8b3f320f193) selected gemini/gemini-4-argon in its
durable generate event but failed on the first model call with model_error /
Model execution failed. No tool or export ran. Gateway shape preflight passes,
but the full hosted workflow is NOT verified working; underlying provider error
still needs diagnosis. No fallback to GPT was silently applied.

Earlier 0.1.6 export invocation failed before graph execution with platform 503
Authorization service unavailable during sandbox provisioning; not an export test.

## Indicator handoff file — 0.1.6

Versioned deterministic alert-indicators/1 export implemented. CLI generated
outputs/extracted_indicators.json from the original test data with stub narratives;
the export itself contains no generated narrative. Sixteen tests pass, covering
contract identity, exact content, successful fake-store write, denied writes and
absence of fabricated file IDs. SGPResourceClient.write_file and ToolLifecycle
verified against 0.50.0 docs/pinned source; consumer FileBlock mapping inspected
on Donovan's reference default branch. Managed probe imports successfully but
cannot send the graph's Harness input. builder_check ready=true/no blockers;
local Semgrep unavailable. Version 0.1.5 already existed remotely, so this release
uses 0.1.6 without overwriting it. Version 0.1.6 is active/latest.
Hosted uploaded-file export test inv_fbf2dca7-722e-4ac9-a3d6-65d58b219137,
thread 82f35095-eeec-4163-a587-66e7c468f557 is still deploying_sandbox, before
agent execution. No managed extracted_indicators.json file exists yet, so hosted
write/download success is not claimed. Local export has 98 observations.

## Selected IOC extraction update — 0.1.4

Added deterministic indicators.observations with requested time_window, src,
dst, protocol, bytes_sent, bytes_received, country, company, src_site, plus full
per-field occurrence references. Full readable table rendered from the same data.
15 automated tests pass, including exact field/path round-trip, overlap, missing
versus null and zero-byte preservation. No fixture bundled. Package ready=true,
no blockers; local Semgrep unavailable. Managed probe still rejects legacy
messages before inference because the graph correctly requires Harness input.
Version 0.1.4 is active/latest. Hosted Harness invocation
inv_0adf50c4-71a4-4e8b-99d1-74dca7ee70f0 returned a reply naming all nine requested
fields and asking for an upload, without inventing analysis. Exact extraction
verified by code/tests with stub upload reader; successful real user-uploaded
file extraction remains unverified until a readable findings upload is supplied.

## Latest update: 0.1.3 user uploads

Published active/latest in staging. Removed fixture/ueba_findings_sim_run2_2026-11-03.jsonl
from deployable source; original workspace fixture preserved. No default dataset.
Harness sources/file parts feed invocation-scoped IDs into a bounded raw-file read
through SGPResourceClient.read_file_bytes (0.50.0 docs and pinned source inspected).
Parser now accepts JSON arrays/single records/findings wrapper as well as JSONL;
JSON provenance uses explicitly labeled 1-based record indices. 14 tests pass.
builder_check ready=true, no blockers; local Semgrep remains unavailable.
Version 0.1.3 hosted invocation confirms missing_upload, and a nonexistent attached
resource confirms 403/file_read_failed with no fallback. Successful real uploaded
findings run is not yet verified; user must attach the file in Donovan.
Donovan resource-part and upload-capability mapping inspected on bundled consumer
default branch; no deployed consumer-version signal or browser verification.

Target: ScaleGov staging. Published agent: `Alert Triage POC`.
Agent ID: `d4ffbfc9-696f-4a5a-b174-75daaa1c993f`. Latest version: `0.1.2`.

## Donovan compatibility follow-up

Version 0.1.2 is active/latest published, adds closed Harness text dispatch and
messages/render_events-only output. Agent discovery tag ps:donovan:chat added
and verified through AMS metadata-containment listing. Hosted Harness fixture
test: 17 accepted, seven groups, seven completed narratives, zero failures.
Small malformed-input test verified exact stored output keys, final AI message,
and durable dispatch/tool/generation events. Twelve deterministic tests still pass.
See DONOVAN.md for IDs, usage, and the registry input_schema=null caveat. No visual
browser verification or cross-tenant access changes were performed.

## Completed

- Scaffold pins: spark-agent-kit 0.50.0, sling-agent 0.1.0.dev6,
  ripgrep-bin 15.2.0. Scaffold-owned requirements were not hand-edited.
- CompletionAgent and ModelConfig APIs checked against 0.50.0 docs and source
  at tag v0.50.0. Module-level authoring object and Harness output preserved.
- `openai/gpt-5.4` passed a streaming/system/tool-schema gateway check.
- Twelve automated unittest checks passed, including UTC grouping, unknown
  severity, schema-path/domain and
  package-import regression checks. They use stub narratives.
- CLI stub run wrote both reports under `outputs/`, explicitly labeled test output.
- Live managed local probe: 17 accepted findings, seven groups, seven completed
  narratives, zero failures; nine gateway calls, zero gateway refusals.
- Earlier live probes correctly failed closed on narrative references and lexical
  domain checks. Added an explicit reference catalog and prevented schema field
  paths such as baseline.mean from being mistaken for domain names. Final probe passed.
- builder_check: ready=true, blockers=[]; verdict unknown because local Semgrep
  is unavailable. Runtime release index availability was not independently checked.
- Version 0.1.0 became active but its first invocation failed before execution:
  AMS imports the graph as a package, unlike the managed probe's direct import.
  Corrected application imports to support both modes, verified package-mode
  imports, reran nine tests and live probe (17 / 7 / seven completed / zero failed).
- Source uploaded and corrected version 0.1.1 publication accepted.

## Hosted verification

- Corrected version 0.1.1 is active and latest in AMS staging.
- Hosted invocation `inv_73824d1b-0a39-4221-8279-1e78b8eb01ed` completed,
  thread `2a075a9c-5cdb-4f2a-b1ef-c24c41ff587f`.
- Stored Harness output contains a successful run_triage tool outcome with
  accepted_findings=17, incident_groups=7, completed=7, failed=0, errors=[].
  Model is openai/gpt-5.4; input hash matches the original fixture. JSON and
  Markdown report are returned in the stored tool result. The API tool display
  truncates the large payload, so this is not a complete manual narrative audit.

## Review cautions

Full inventories are large; the outer chat context middleware warned that a large
tool response was reduced. The stored tool output is authoritative, not the final
chat summary. End-to-end durable report download/UI projection is not implemented.
No claim of live prompt-injection robustness or complete semantic fact-checking.
Local output files currently contain STUB results, not saved live narratives.

Original fixture SHA-256:
`6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`.
