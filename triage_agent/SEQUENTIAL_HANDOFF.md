# Sequential handoff design and release evidence

> Historical two-stage design/release ledger (0.1.18–0.1.19). Current production
> uses five separate submission/collection stages and includes Recommendation;
> follow [DEMO.md](../DEMO.md) for current budgets, versions and run instructions.
> The policy below is preserved as implementation history, not the current runbook.

## Policy defined before implementation (2026-11-09)

- Direction is Triage → Historical Enrichment (`420e63bd-8220-48bd-bada-743f0daea46c`, latest published). No receiver change or schema migration.
- Only this call's `indicator_export.status=created`, nonempty returned ID and SHA-256 qualify. At least one accepted finding is required. Empty/invalid input may still produce the existing diagnostic export, but does not dispatch. Partial extraction/context is allowed and retained unchanged.
- The exact confirmed export ID goes in the receiver's strict Harness `sources` resource. Never search filenames, read old messages for input, or use the original findings ID.
- Use public Agent Kit 0.50.0 `AMSRemoteAgent.ainvoke`, a separate client and fresh config per call, published lifecycle, injected `AMS_API_URL` (or injected `MCPX_CHECKPOINT_URL`). No compiled host fallback, credentials, custom identity headers, direct POST or shell execution.
- HTTP timeout 30s, poll interval 2s, SDK polling budget 90s, overall downstream budget 120s including output verification, plus at most 5s of read-only reconciliation after failure. Zero submission retries and zero file-write retries. Read polling is not resubmission. Timeout does not cancel the child. A lost submission response is `unknown`, even when IDs are unavailable; an acknowledged submission retains both IDs for operator reconciliation.
- Fresh request → one registered tool execution → at most one child submission in normal execution. Existing file-first routing stops after its current tool result. New explicit requests, including identical uploads, are independent runs with new exports/child threads. No global content cache or cross-user deduplication. No server idempotency key is documented by this SDK. Process death/checkpoint replay in the additive-write window cannot guarantee exactly-once effects; do not automatically replay/retry uncertain operations. Operator reconciliation is required before deliberate retry. This is not crash-safe distributed exactly-once orchestration.
- Never pass the parent thread ID as the child's continuation ID. Record parent thread/invocation when supplied by runtime config, tool-call ID, child thread/invocation, exact file ID/hash in the parent's tool result. Platform IDs remain authoritative; missing parent IDs are null, not inferred.
- Preserve original triage/export status regardless of downstream failure. Platform status is independently read from the exact child invocation. Enrichment application status comes from its code-owned `run_enrichment` tool result, not AI prose. Verify its receipt ID/hash before exposing any downstream files. Export references must agree with its confirmed Harness FileBlocks. No arbitrary remote text is added to the parent status.
- Parent public channels stay `messages`, `render_events`. Existing Triage FileBlock is retained; verified child files are additional FileBlocks on the tool outcome. AWS remains disabled: expected application status `partial`, history `not_configured`.

## Version-matched authority

- [AMSRemoteAgent 0.50.0](https://scaleapi.github.io/spark-agent-kit/reference/agents/#spark_agent_kit.agents.remote.ams.ams_remote_agent.AMSRemoteAgent): invocation IDs, fresh configs, output projection, managed identity.
- [Tool lifecycle 0.50.0](https://scaleapi.github.io/spark-agent-kit/how-to/output-customization/#extend-action-payloads-and-content): “Harness still creates the event envelopes and controls action IDs, pairing, ordering, and persistence.”
- Read pinned source `v0.50.0:src/spark_agent_kit/agents/remote/ams/ams_remote_agent.py` and `remote_agent.py`: SDK submits `/v1/threads`, with no submission retry; fetches `/v1/invocations/{id}/output`. This supersedes the older agent-egress reference's `/agents/{id}/invoke` recipe.
- Read bundled MCPx default-branch `checkpoint_policy.go`: checkpoint host is platform-managed; current deployment rewrites it through managed egress. Live hosted acceptance remains necessary.

## Verification / release

Pre-edit baseline: 32 tests ran, 30 passed, two SDK checks skipped in ordinary CLI Python. AMS staging/platform verified Triage 0.1.17 and Enrichment 0.1.0 active/latest. Release acceptance pending.

Local implementation check: 38 tests ran, 35 passed, three SDK-only tests skipped (ordinary CLI is Python 3.9.6, SDK absent). New tests exercise exact file/hash transfer, independent repeated requests, missing/invalid/empty input, uncertain writes without retry, partial context/input, downstream errors, acknowledged/unacknowledged timeouts, receipt mismatch and action-scoped FileBlock checks. Added SDK MockTransport regression for task-only marshalling; it is among the skipped tests, not claimed executed.

`builder_probe` imported/constructed the graph in managed 0.50.0, then failed before execution because the probe supplies messages rather than strict Harness task input. No production contract weakening. `builder_check` ready=true, zero blockers, security verdict unknown because local Semgrep is unavailable. Existing Argon model passed `builder_env(model=...)` request-shape validation.

Published 0.1.18 source bundle `75d97033-5bfd-49bf-995f-bc09e3827150`; found and corrected client coercion before hosted acceptance: remote input schema must derive from AgentState, not ChatAgentState, whose pinned `coerce_input_state` requires messages. Corrected 0.1.19 source bundle `7529cf8a-a9c4-4578-9f49-2941fdb70c3b`. No Enrichment source/release or historical snapshot edited.

0.1.19 verified active/latest. Hosted no-file invocation `inv_2e07670b-6708-4e45-8413-8fc45b593e10`, thread `7cc3d7d8-3748-4862-ac6d-0466bb4a7e87`, completed with `missing_upload`, zero FileBlocks, public `messages`/`render_events`, paired durable tool action/outcome and final dispatch outcome.

Full sequence started: `inv_c1274578-e198-49a3-9b1a-92a3323da108`, thread `fba0dfa0-7ced-4d9e-910f-158892fed5f8`, verified version 0.1.19. Synthetic findings upload `61827a37-3cb1-4a13-8445-cdf1e5ad8ded` is the existing original input, not an export selected by name. Its size is 62,315 bytes and content route shows the synthetic findings. Metadata MD5 differs from the local same-named fixture; do not claim byte-identical local/hosted inputs. Current run's export digest/receiver receipt must be used for handoff acceptance. Poll this exact invocation, do not invoke again to wait. `builder_invoke` without input cannot poll despite its running-response suggestion; use read-only invocation/output routes.

Enrichment regression: 24 tests ran, 22 passed, two SDK checks skipped; `prepare_pod.py --check` passed. No receiver edits required.

### Hosted acceptance PASSED

- Parent completed at `2026-11-09T17:30:45.766624Z`; 17 accepted findings, seven groups, 98 observations, six context successes and one explicit 90s context timeout; application `partial`. Input SHA-256 is `6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`, matching the local synthetic fixture despite the metadata-MD5 discrepancy.
- This invocation's created export: `53a024fc-ce09-43c9-88f2-2602c68746e0`; exact serialized UTF-8 SHA-256 `ba6ec604f592b92dac2534f87e10f0ef0bb766ef74de3c3131f720796d0f5e36`.
- Child `inv_39688264-d706-437f-baa6-2dca2cdaefe8`, thread `1591e706-4f8f-46ba-aedd-4aa719357361`, version 0.1.0, created `17:30:36.111725Z`, completed `17:30:44.794473Z`. Direct invocation read confirms strict dispatch `sources` contains **53a024fc…**, not original findings **61827a37…**. Receiver receipt confirms the same ID and SHA-256. Parent records `attempts=1` and correct parent/child correlation IDs.
- Child platform `completed`; application `partial`; 323 queries planned, all 323 `not_configured`, zero historical searches/match claims; export status `completed`.
- JSON `49e98d14-257a-458f-b71d-c62478ec9544`, 274,809 bytes, MD5 `f2d92cb43fe2ee7f56e9abf5d5fd1175`; Markdown `2eeb2391-eea7-4277-bbce-9cd476035cd1`, 79,968 bytes, MD5 `3c27292bcf13462b9e4624c99e5720a3`. Both independently return file metadata 200.
- Read both exact invocation output projections: only `messages` and `render_events`. Child has paired `run_enrichment` action/outcome with two FileBlocks; parent's paired `run_triage` outcome has its export plus both matching downstream FileBlocks. Both final dispatch outcomes are `graph_completed`. Parent progress durably records file confirmation before downstream invocation. Confirmed through stored output, not only streamed deltas.
- Same-parent-thread text-only follow-up `inv_d06eb5ed-fac2-4365-83c6-805235a1a89c` completed `missing_upload`; no stale attachment used. Repeat requests with attached files tested locally as independent fresh exports. Hosted fault injection and crash replay not performed.
- Child thread lineage confirms export-file → child invocation and original findings → export-file edges. No direct parent-invocation → child-invocation edge returned; explicit recorded IDs provide correlation. Classification propagation remains unresolved (child file metadata tags null); synthetic UNCLASSIFIED test does not approve broader marked-data handling.

No Git commit. No Enrichment release, source snapshot, extraction schema, model behavior or unrelated review fix changed. Local security scan remains unknown; hosted activation is not a clean-scan attestation. Three SDK-only tests remain locally skipped; hosted success directly exercises remote marshalling and FileBlock projection. Donovan UI was not manually tested. Crash-safe idempotency remains a limitation, not an implemented guarantee.
