# Bounded read-only collection retries — 2026-11-10

> This ledger records the **Dev** implementation/release, including its pending
> acceptance checkpoint. It does not establish current Dev status; this cleanup
> inspected staging only. The same polling change was subsequently promoted with
> staging receiver IDs in [staging 0.1.24](STAGING_RELEASE_2026-11-10.md).

## Scope and diagnosis

Confirmed AMS profile `scalegov-dev`, tenant `69dfa4b844ff488d98b2674f`
before live reads/publication. Entry baseline 0.1.24 was active/latest.
Only production `plugins/alert_triage/stages.py` changed; tests are agent-scoped.
No staging changes, downstream redeploys, VoF migration, fixture/snapshot/history
rewrites, dependency patches, model fallback, inference-timeout changes or commit.

Observed parent `inv_bd6bb221-e67c-405d-9e4b-5618178c0b20` stored output
confirms `collect_enrichment` stopped after 20.717s with
`collection_failed_uncertain`, retaining its Triage artifact and child ticket
`inv_2f18bb30-aa76-4df6-836b-abeee10d4e77`. Recommendation was not submitted.
The exception was not recorded: no underlying polling cause is established.
The separately reported 12 Argon inference timeouts and Envoy 503 are not
diagnosed or fixed by this polling change.

## Policy

- Retry seam is only GET status and GET output for the checkpointed invocation.
  No SDK resubmission, replacement thread/invocation, or automatic file-write retry.
- Allow `httpx.ConnectTimeout`, `httpx.ReadTimeout`, the GET's hard wall-clock
  timeout, and HTTP 429/500/502/503/504. Other transport failures (including
  generic ConnectError/ReadError, TLS/connect failures, write/pool timeouts),
  redirects, authentication/authorization and other HTTP errors fail closed.
- At most **three retries total across the collection**, not reset by successful
  polls, with **1/2/4s** backoff. Normal pending/204 polls retain the 2s interval.
- Each GET has HTTP phase timeout and hard async wall-clock timeout bounded to
  `min(30s, remaining deadline)`. Existing 90s/720s collection limits remain;
  outer async cancellation enforces the overall deadline. No new GET starts
  after deadline; a wait that cannot fit stops immediately as deadline-limited.
- Retry-After accepts bounded integer-seconds or timezone-aware HTTP-date input;
  malformed values fall back to local backoff. Use the larger of backoff and
  server delay. Never retry earlier than a valid server delay. If over 10s,
  stop `retry_after_exceeds_bound`; if it cannot fit, stop `deadline_exceeded`.
- Validate ticket identifiers/path safety and SHA-256 before reading. Parsing,
  status/schema and existing exact receipt/action-scoped attachment checks are
  outside the retry seam. Invalid data is not retried or trusted.
- Existing uncertain/incomplete outcomes, submission `attempts`, strict Harness
  input/output, v3 schemas, five stages, extraction-only default, AWS unavailable,
  Dev receiver IDs and human-review/no-actions boundaries are preserved.

`polling_diagnostics` records total GET attempts, actual retry attempts, a bounded
list of fixed error categories, fixed stop category and elapsed seconds. Stage
diagnostics remain separate. No raw exception messages, bodies, headers, URLs or
credentials are retained in diagnostics. Final collection logs contain only fixed
category, counts and elapsed time. Prior confirmed artifacts remain in earlier
stage checkpoints; uncertain collection publishes no unverified child artifacts.

## Verification

- Reviewed SAK `v0.50.0` source
  `src/spark_agent_kit/agents/remote/ams/ams_remote_agent.py`; no dependency edits.
  Existing one-shot SDK submission is unchanged. Public reference:
  [AMSRemoteAgent — 0.50.0](https://scaleapi.github.io/spark-agent-kit/reference/agents/#spark_agent_kit.agents.remote.ams.ams_remote_agent.AMSRemoteAgent).
- `builder_scaffold` adopted existing pod with **no files created/replaced**;
  scaffold pins and graph construction preserved.
- Managed `builder_probe` on local-only `tests/reliability_verify`:
  **60 Triage + 15 Recommendation tests passed, zero skips**, followed by
  mocked five-stage graph/checkpointer run with five confirmed FileBlocks.
  Reply: `SDK tests and five-stage checkpoint workflow passed`.
- New `tests/test_polling.py`: 12 tests cover status/output recovery for each
  allowed transient type/status, collection-wide exhaustion across successful
  polls, fake-clock deadline/backoff/per-request bounds, real hung-GET cancellation,
  safe Retry-After parsing/bounds, permanent failures, invalid tickets/data/receipts,
  Recommendation count integrity, 204 race, child terminal failures, cancellation,
  preserved upstream artifacts/incomplete routing, and submit-once recovery.
  Mocks forbid any collection submission and assert exact invocation URLs.
- Initial additional preservation test used an incomplete mock ticket lacking
  platform_status; corrected the test fixture to match real submission tickets,
  then reran all managed tests successfully. No production routing change.
- Ordinary CLI initial run: 58 discovered, 44 passed, 14 dependency-related skips;
  this preceded two added tests. Managed results above are the complete gate.
  Final ordinary CLI rerun: 60 discovered, 44 passed, 16 dependency-related skips,
  zero failures. No dependency installation was used to hide these skips.
- Generic production probe rejects messages-only input before inference
  (`fault=harness`, zero gateway calls), expected with strict Harness; validation
  was not loosened to accommodate the generic probe.
- `builder_check`: **ready=true**, no blockers. Semgrep absent: local security
  scan **unknown**, not a clean security attestation. Existing empty fixture,
  runtime/index and static model-check unknowns remain. Argon is in the live
  catalog; managed verification passed without changing production inference.

## Deployment checkpoint

Published entry only as **0.1.25**, agent
`7f244b84-ff27-43b0-a629-99a76791373a`, retained bundle
`cb31d9ff-102f-404a-be1d-54aa9905c3f3`.
Activation and hosted acceptance are recorded below when confirmed.

### Hosted verification

- `builder_status`: 0.1.25 **active/latest**, 0.1.24 active/not-latest.
  Deployment ID `65eeb42b-281a-48a6-9bf0-ef8228097734`.
- Agent metadata retains `ps:donovan:chat`, one required upload, 1,000,000-byte
  limit and original MIME list. Publish defaulted display name to the absolute
  local source path; a metadata-only PATCH restored **Network Investigation Demo**
  and returned active 0.1.25 with unchanged discovery/upload metadata. No republish.
- Hosted strict-Harness missing-file acceptance:
  `inv_a0c49bcd-62e1-44ab-81de-80b8f42a3f87`, thread
  `f499092d-18d1-4162-9580-ec0436ab5c84`, completed with explicit incomplete/no
  analysis and request for an original findings attachment. Existing generic
  final wording mentions a possibly-running child even when none was submitted;
  this pre-existing presentation imprecision was not changed in the polling fix.
- Full-chain acceptance submitted **once**, fresh thread
  `904eed78-e0b3-46b6-a48d-6ef6ffb6c519`, invocation
  `inv_0860c6c6-2d7a-4f10-bdd9-1e4edba88d66`, version 0.1.25.
  Input explicitly attached existing Dev file
  `475f3738-eeda-4754-8658-c8854e1c323a`,
  `ueba_findings_sim_run3_subtle_2026-11-03.json` (81,591 bytes), the synthetic
  upload used by the observed failing run; not the different local run2 fixture.
  Created `2026-11-10T19:13:03.171884Z`, started `19:13:10.714238Z`.
  Follow-up monitoring uses only invocation/output GETs, never resubmission.
  The typed invoke tool's suggested thread-only polling call returned
  `message or input is required`; it did not create a second invocation.
- Missing-file stored output contains exactly `messages` and `render_events`,
  with durable run_triage action/outcome and `missing_upload`; no child submit.
- Read-only downstream/thread inspection confirms Enrichment
  `inv_bd68a940-4944-4091-b1b6-05b160f857d8` (thread
  `6fc9160d-33e8-4bc3-bbe5-e7e2f5e5e1c5`, version 0.1.2) completed at
  `19:13:21.021049Z`, using new Triage file
  `6296b95b-b82a-4bb1-8ede-fc670af5a600`.
  Recommendation `inv_3b4b9826-8e35-4449-9e57-69d20692b6bc` (thread
  `b01d4d15-110f-4f66-94db-2e0792b5af89`, version 0.1.3) started at
  `19:13:28.991915Z`, using new Enrichment JSON
  `b5dbec0f-3c27-4aab-bda9-8ffa37397427`.
  Thus the hosted path progressed beyond Enrichment collection; this alone does
  not prove a transient fault occurred or a retry was needed.
- While running, both parent invocation and thread `/output` reads returned only
  the initial dispatch event/checkpoint, despite downstream progress evidenced by
  invocation records and lineage. No conclusion about missing stage checkpoints
  or successful final projection is drawn before terminal output.
- Enrichment terminal output independently confirms exact Triage receipt SHA-256
  `fc484923ccabe3c07f20a478433c84a90d9d54568d8315b3d51e08b18a29feb6`,
  `alert-indicators/3`, partial status, 530 `not_configured` criteria and zero live
  historical searches, plus action-scoped JSON/Markdown FileBlocks. Markdown ID:
  `23d5031c-5eff-4250-94db-799f1da7b308`.
- **Acceptance still pending at this handoff (~19:16 UTC):** parent and
  Recommendation remain running. No terminal five-file result, hosted retry
  count or full-chain success is claimed. Do not submit another run to poll.
  Continue read-only `GET /v1/invocations/{id}` for the parent/Recommendation IDs
  above, then read parent `/output` on termination and check five stage messages,
  polling diagnostics, receipts, file events and explicit partial/incomplete text.
  Existing Recommendation 720s collection budget was not increased. If output
  remains dispatch-only after terminal completion/read-after-write reconciliation,
  escalate to MCPx with these IDs rather than changing inference or resubmitting.

Downstream baseline reads: Enrichment 0.1.2 and Recommendation 0.1.3
active/latest. No downstream publication was requested or performed.

## Limits

Fault recovery is proven by deterministic injection, not live fault induction.
Retries do not guarantee eventual success, exactly-once crash recovery or child
cancellation. Exhaustion/deadline/permanent failures require reconciliation before
deliberate resubmission. Hosted success is not a reliability SLA, narrative semantic
audit, vulnerability remediation or proof of marking propagation. Existing managed
runtime warnings about checkpoint deserialization registration remain out of scope.
