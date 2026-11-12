# Reliability work checkpoint — 2026-11-09

## Current reading guide

This is the historical five-stage/concurrency implementation ledger. For the
later staging 0.1.24 polling promotion see [release](STAGING_RELEASE_2026-11-10.md)
and [retry policy](POLLING_RETRIES_2026-11-10.md). Current tests and hosted failures
are summarized in [EVALUATION.md](../EVALUATION.md); older “latest” claims below
apply only to their recorded checkpoints.

## Historical finalized checkpoint — 2026-11-10 UTC

Implementation released as Triage 0.1.22 / Recommendation 0.1.2; AMS subsequently
automatically rebuilt them as 0.1.23 / 0.1.3 with the same source bundle IDs.
Enrichment is now 0.1.2. All three active/latest at documentation verification.
Latest operator-confirmed full-chain run `inv_b394de1e-5e49-4616-8495-f936041f9844`
completed in 206.181s, five files, 7/7 recommendations, zero input/model failures.
Triage context was intentionally deferred; AWS history stayed not_configured.
See [current runbook](../DEMO.md) for exact receipts, child IDs and timings.

The earlier acceptance `inv_5cd183b6-4312-4858-aad3-489da7fe4d1a` also completed:
created Nov 9 23:58:05.247496Z, completed Nov 10 00:00:14.054933Z (~128.807s),
7/7 Recommendation analyses and five attachments. This did not prevent the
subsequent Enrichment 0.1.1 security takedown. Same-digest rebuilds have not proven
libexpat1 remediation; see Enrichment's image investigation. The generic probe's
messages mismatch was not fixed by weakening production Harness validation.

Historical pending/not-yet-published statements below are superseded by this
checkpoint. No fresh inference, release or code change in documentation cleanup.

Operator authorized ordered implementation: stage checkpoints, diagnostics,
extraction-only Triage, then Recommendation concurrency two.

Local implementation (not yet hosted-verified):
- stages.py splits extraction, Enrichment submission/collection, Recommendation
  submission/collection into distinct CompletionAgent tool turns. Each returned
  result/attachment and child ticket can checkpoint before the next step.
- Public AMSRemoteAgent stream starts a child and observes acknowledgement, then
  closes observation; collection uses read-only invocation APIs, never resubmits.
- Cancellation is logged and re-raised. Stage result has elapsed time and fixed
  error codes, with no provider error text. Hard process death cannot be caught.
- ExtractionOnlyClient preserves the exact observation IDs/rows and extraction
  summary, marking v3 narrative context unavailable with narrative_deferred.
  No stub narrative is used. Legacy failed counters represent deferred context;
  user-facing status explains this explicitly. Default staged demo mode is
  extraction-only; TRIAGE_EXTRACTION_ONLY=false restores live Triage inference.
- Tests: Triage 48 ran, 44 passed, four dependency/SDK checks skipped.
- builder_probe imported the graph but legacy messages input failed strict
  Harness validation before execution. Contract not loosened.
- builder_check ready=true, local security scan unknown (Semgrep unavailable).

Deployment collision: attempted 0.1.21 publish refused because that version already
exists. Live read then showed Triage 0.1.21 and Recommendation 0.1.1 active/latest,
not versions deployed by this implementation turn. Reconciled through exact-version
GET responses: config.base_image_rebuild.rebuilt_by is ams-base-rebuilder, with
rebuilt_from 0.1.20 / 0.1.0 respectively. Both retain the original source bundles.
These were automated platform base-image rebuilds, not operator source changes.
Triage created_at 19:00:41.358328Z; Recommendation 19:00:41.017050Z. This overlaps
the 19:00:39–19:00:42 failure window and warrants lifecycle investigation; it does
not independently prove rebuild-triggered termination. User confirmed no manual
publication. Future implementation releases should use unused versions 0.1.22 and
0.1.2 after final verification, not overwrite the rebuild versions.

Known remaining verification requirements:
- Real Harness multi-tool/checkpointer regression, SDK stream acknowledgement and
  close semantics, cancellation/collection failures, and partial attachments.
- Confirm graph recursion budget supports five tool turns (do not assume defaults).
- Enrichment and Recommendation contract acceptance of extraction-only export.
- Recover IDs across acknowledged submissions, no automatic retry on uncertainty.
- No claim of distributed exactly-once execution or automatic crash recovery.
- Source comparison/release reconciliation, then staged hosted acceptance.

Recommendation concurrency code/tests live only in recommendation_agent; see its
RELIABILITY_WORK.md. Historical snapshots/outputs preserved; no Git commit.

## Hosted repair and release

Direct Enrichment test reproduced 409 VERSION_NOT_READY. Exact-version evidence
shows Enrichment 0.1.0 was marked compromised for libexpat1 CVEs at 19:00:05Z,
taken down at 19:00:08Z, image deleted at 19:00:12Z, rebuild skipped not_candidate.
No active Enrichment version remained. This explains the current admission blocker;
the original 409 trace did not preserve its response body, so the historical code
is corroborated by timing/current reproduction, not directly recovered.

Published unchanged source 957c7e7c-af75-4b38-bc6f-dafc077fc983 as Enrichment
0.1.1 on the current platform base. Active/latest; direct handoff invocation
inv_01e993b4-10ff-440a-b495-bafc70a32355 completed with 323 not_configured and
two exports. No Triage inference repeated; no old vulnerable image reactivated.

Local SDK verification runner tests/reliability_verify (never publish) passed all
48 Triage and 15 Recommendation tests without skips, plus five-stage actual graph
execution with InMemorySaver and five stage FileBlocks. No explicit recursion
override was necessary for the real graph under default local run config.
The simulated child transport does not prove hosted broker/SSE behavior.

Triage 0.1.22 active/latest; bundle b0562145-fe1e-4c14-b2e0-1c7dcc20272d.
Missing-upload smoke inv_6d8d9bbd-0cd3-482b-b8e4-1698211732db completed with
INVESTIGATION INCOMPLETE, no fabricated analysis. Full-chain acceptance pending.
Recommendation 0.1.2 submitted, deployment initially pending.

Recommendation 0.1.2 subsequently active/latest. Managed verification passed all
63 tests without skips and confirmed five stage FileBlocks in actual graph output.
Full-chain hosted acceptance submitted exactly once:
inv_5cd183b6-4312-4858-aad3-489da7fe4d1a, thread
b449ad19-cce3-4a3f-adf3-addaa40a6117, using original upload
a94a1f35-c68f-45fd-8961-85b6d3a320ef. Running at checkpoint; no success or speedup
claim until final output and child receipts are checked. Poll, do not resubmit.
