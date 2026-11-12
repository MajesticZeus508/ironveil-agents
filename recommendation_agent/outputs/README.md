# Preserved local examples

These directories contain actual local Argon outputs on **synthetic Enrichment
examples**, not the hosted seven-incident acceptance files or live AWS results.
Each contains recommendation_results.json and recommendation_report.md.
Keep original bytes and paths; do not regenerate old reports during housekeeping.

| Directory | Result / purpose |
|---|---|
| `live_2026-11-09T15-40-59.360645+00-00_verified_demo/` | Earlier failure: narrative validation rejected; evidence retained, run partial |
| `live_2026-11-09T15-41-19.374993+00-00_aws_pending/` | Earlier successful narrative with unavailable history; run partial |
| `live_2026-11-09T15-42-09.454449+00-00_verified_demo/` | Final schema-bound complete synthetic-history example; analysis/run completed |
| `live_2026-11-09T15-42-32.172014+00-00_aws_pending/` | Final schema-bound AWS-pending example; analysis completed, run partial |

The last two are the preferred local examples. All predate the subsequent fixed
report decision gate and additional upstream metadata preservation. Their model
prompt/client match the final schema-bound test at that checkpoint; they are not
a byte-for-byte example of the final published report renderer.

Known model-quality cautions: some prose infers connection establishment or suggests
closure too quickly. A passing validator is not a semantic endorsement. Human
corroboration of authorization, scope and absence of conflicting evidence is required.

Hosted receipt/status/attachment evidence is summarized in
[`hosted_acceptance_0.1.0.json`](hosted_acceptance_0.1.0.json), with release context in
[`../VERIFICATION.md`](../VERIFICATION.md). It is a selected non-secret evidence
record from API inspection, not a raw thread dump or downloaded report-content audit.

Latest hosted five-run results are indexed in the
[staging ledger](../../triage_agent/STAGING_PERFORMANCE_2026-11-11.md), not these
older one-incident local examples. The 25 hosted files are not fully downloaded
into this workspace; [recovery gaps](../../AMS_INVENTORY.md) remain explicit.
