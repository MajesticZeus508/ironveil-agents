# IronVeil Investigation — Start Here: operator runbook

**This is the user-facing entry point for the full IronVeil workflow**, not just
the triage stage. It performs triage and calls **IronVeil Historical Enrichment**
then **IronVeil Recommendations** automatically, returning their analyst reports.
The supporting agents are not separate starting points for normal users.

**Proof of concept:** approved synthetic data only, AWS history unavailable,
human review required, no response actions executed.

Staging display names and descriptions were updated on 2026-11-12 without a new
release or changes to IDs, source bundles, discovery metadata or behavior.
Former names in historical evidence are Network Investigation Demo,
Historical Enrichment POC and Recommendation Agent POC, respectively.

Live release state rechecked during housekeeping; latest evaluation **2026-11-11 UTC**.
ScaleGov staging / `platform`
(`6a1099f9e1ca37ee1216d8c3`). Deployment state is a checkpoint, not a guarantee.

## Deployment map

| Agent | ID | Active/latest | Retained source bundle |
|---|---|---|---|
| **IronVeil Investigation — Start Here** (entry point) | `d4ffbfc9-696f-4a5a-b174-75daaa1c993f` | 0.1.24 | `b06c9ba3-3223-4bdb-8281-61fba2bab92e` |
| IronVeil Historical Enrichment (supporting) | `420e63bd-8220-48bd-bada-743f0daea46c` | 0.1.3 | `2eb071f0-fe65-4d6f-a477-17819787f720` |
| IronVeil Recommendations (supporting) | `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f` | 0.1.4 | `eb82adf2-8f84-4008-9da8-48bdbe6b929b` |

Entry 0.1.24 promotes bounded read-only polling retries; both receivers were
rebuilt unchanged after the operator-reported base-image fix. See
[release evidence](triage_agent/STAGING_RELEASE_2026-11-10.md).
Local staging entry source is `triage_agent/releases/staging_0_1_24/`;
`plugins/alert_triage/` targets Dev. See [backup scope](AMS_INVENTORY.md).
Only the entry application has the Donovan discovery tag `ps:donovan:chat`.

## Operator run

1. Refresh Donovan staging; select **IronVeil Investigation — Start Here** and start a fresh chat.
2. Attach `triage_agent/staging_input_verification.json` relative to this
   workspace. It is JSONL content despite the `.json` extension: 62,315 bytes,
   17 synthetic findings. This is the hash-verified preserved run2 input; the older
   documented filename is absent locally. Entry limits: one file, 1,000,000 bytes, 100 records;
   JSON, NDJSON or plain-text upload metadata.
3. Ask: **Run the network investigation and produce analyst recommendations.**
4. Allow several minutes. Do not resubmit to poll a running request.
5. Open `recommendation_report.md`. Expected attachments: Triage JSON,
   Enrichment JSON/Markdown, Recommendation JSON/Markdown (five total).

Upload original findings, not `extracted_indicators.json` or
`enrichment_results.json`. Missing/malformed/wrong-stage input does not fall back
to samples or stale attachments. Fresh requests require explicit uploads.

## Implemented behavior and controls

Schemas: `swoop-ueba-finding/1` → `alert-indicators/3` → `alert-enrichment/1`
→ `alert-recommendations/1`. No v4 migration or new intelligence source.

The entry uses five separate checkpoint-sized tool turns:
`run_triage`, `submit_enrichment`, `collect_enrichment`,
`submit_recommendation`, `collect_recommendation`. Returned tickets, stage results
and confirmed attachments can persist before the next stage.

- Triage defaults to deterministic extraction only, with **zero Triage inference
  calls**; narrative is deferred to Recommendation. Existing v3 unavailable/failed
  context fields and legacy failed counters disclose `narrative_deferred`, not
  lost extraction. `TRIAGE_EXTRACTION_ONLY=false` restores live Triage context.
- Enrichment prepares logical history criteria; AWS/S3/query engine/IAM/egress
  remain unconfigured. `not_configured` is not a historical search or negative.
- Recommendation uses Argon, one call per incident, concurrency bounded to two,
  original ordering preserved, 90s request / 95s active-call bound, zero retries
  and no fallback. No inference is added for outer routing.
- Submission observation budget: 40s. Collection: 90s Enrichment / 720s
  Recommendation, HTTP timeout 30s and poll interval 2s. These are separate stage
  budgets, not the legacy monolithic 120s/780s overall bounds.
- One submission per child in normal execution, fresh thread/config, no automatic
  submission or file-write retries. Closing observation does not cancel the child.
  Timeout/uncertainty requires reconciliation before deliberate retry.
- Read-only status/output GETs allow at most three transient retries across each
  collection, 1/2/4s backoff within the existing deadline; bounded Retry-After.
  Integrity/schema/auth errors are not retried. This never resubmits a child or
  retries inference or file writes. See [policy](triage_agent/POLLING_RETRIES_2026-11-10.md).
- Current-run exact file IDs, byte SHA-256 receipts, schemas and action-scoped
  FileBlocks are checked before downstream files are trusted/projected. Children
  use latest published versions, not fixed semvers.
- Completed upstream files survive downstream errors; incomplete stages are
  labeled **INVESTIGATION INCOMPLETE**. Platform completion and application partial
  status are separate. There is no distributed exactly-once or automatic
  crash-recovery guarantee.
- Human review required; no actions executed. Supplied company/country labels and
  model hypotheses are not independent corroboration. Data-marking propagation
  remains unresolved: use approved synthetic demo data only.

## Latest evaluation and known failure

The five sequential staging runs on 2026-11-11 completed every stage and returned
five files each, but only **28/35 analyses succeeded** (six timeouts, one validation
rejection). Parent median **190.490s**, range **162.103–209.962s**; only one run
achieved 7/7. Latest run returned 6/7. [Team evaluation](EVALUATION.md) and
[exact ledger](triage_agent/STAGING_PERFORMANCE_2026-11-11.md) are authoritative.
These are not semantic-quality scores or SLAs.

The first 0.1.24 acceptance stopped at the managed Enrichment JSON read/receipt
guard, before Recommendation submission. Three upstream files survived. A second
test succeeded 7/7 in 143.886s; subsequent success does not diagnose the first
failure. Reconcile child IDs before a deliberate retry; do not bypass integrity checks.

## Historical operator-confirmed Donovan run — 0.1.23

Operator confirmed Donovan success; matching stored output and parent/child
invocation records were read through AMS, without launching another run.

- Parent: `inv_b394de1e-5e49-4616-8495-f936041f9844`, Triage 0.1.23.
- Thread: `5185a5b7-9964-4c5d-9e52-f29405619cce`.
- Created `2026-11-10T02:09:06.495751Z`; started `02:09:11.566776Z`;
  completed `02:12:32.676409Z`.
- **206.181s end-to-end; 201.110s after start; 5.071s startup/admission.**
  Excludes browser upload/render/download. Batch averages: **12.13s/finding**
  (17 findings), **29.45s/incident** (seven groups), not individual call latency.
- 17 accepted findings, seven groups, 98 observations, zero input errors.
- Enrichment 0.1.2: `inv_6ad508d1-fc73-43d5-a681-6ed42b46d45e`,
  thread `46dfb5be-e490-4d53-bcca-1eae05169a74`, platform completed.
  Child creation-to-completion 8.310s; active execution 2.954s.
- Recommendation 0.1.3: `inv_7eb8f911-ed1f-47cb-97ae-351aa42eef06`,
  thread `6c85e3ea-47a3-491f-9617-e124413ef245`, platform completed,
  7/7 analyses, zero failures. Child creation-to-completion 174.454s;
  active execution 168.208s.

Parent stage diagnostics (include observation/collection overhead, not solely child
compute): Triage 1.537s; Enrichment submission 20.994s + collection 0.137s;
Recommendation submission 7.875s + collection 169.124s. Remaining ~6.514s includes
startup and other orchestration. Do not add child durations to parent durations.

| Output | Confirmed file ID |
|---|---|
| extracted_indicators.json | `969c7c66-13b9-4dbb-a4c2-1e5196651eaa` |
| enrichment_results.json | `495a9a58-e68a-4cbf-87e1-46700e12f212` |
| enrichment_report.md | `45968bb7-db1d-49ca-b719-bed76b8b26af` |
| recommendation_results.json | `25fed65e-942d-48f7-be85-a351e3cf43b4` |
| recommendation_report.md | `9ccc6a9b-1ae1-48a6-a180-82ea522a5e6c` |

Triage receipt SHA-256:
`b4676c83c971852ef74318f122b2077014a249c840579781682ab758dda24c63`.
Enrichment JSON receipt SHA-256:
`ac45d90b621df93029c6078a986dd1aa24b04174301ef24d182b520e21fda560`.
Final output matches the operator screenshot and retains `partial`, AWS
`not_configured`, deferred upstream narrative and human review. Full narrative
semantic auditing is not claimed. One success is not a latency/reliability SLA.

## Verification and security boundaries

Latest recorded managed regression: 60 Triage + 15 Recommendation tests passed
without skips, plus a mocked five-stage graph/checkpointer run with five file
blocks. This is distinct from hosted acceptance. Ordinary CLI may skip SDK checks.
Local packaging reported ready=true; Semgrep was unavailable, so local security
scan status is unknown. See each agent's verification/reliability documents.

Fresh ordinary-CLI regression: Triage **60 / 44 / 16 skipped**, Enrichment
**24 / 22 / two**, Recommendation **15 / 14 / one**. Total **99 discovered,
80 passed, 19 skipped**, zero failures after correcting test-only fixture paths.
Python 3.9.6 is below the documented 3.11+ support floor; SDK/httpx checks skip.
Enrichment freshness passed. See [evaluation](EVALUATION.md) for scope and limits.

**Functional success is not a verified image-security fix.** Enrichment 0.1.0/0.1.1
were taken down for libexpat1 2.9.0-r0; fixed version listed as 2.10.0-r0.
Historical Enrichment 0.1.2 reported the same digest as 0.1.1; current 0.1.3 has
a different digest in the release record. No SBOM/fresh-scan proof of remediation
is available here. An engineer's Slack message supplied by the operator identifies the
staging base-image issue as platform-owned, tracked in **PSP-3646**; ticket state
was not independently checked. No waiver, restore or security bypass was used.
See [Enrichment security investigation](enrichment_agent/IMAGE_SECURITY_2026-11-10.md).

Historical two-stage and initial demo release evidence remains in
[SEQUENTIAL_HANDOFF.md](triage_agent/SEQUENTIAL_HANDOFF.md),
[RELIABILITY_WORK.md](triage_agent/RELIABILITY_WORK.md) and agent verification
ledgers. Documentation cleanup does not publish, change source behavior, regenerate
evidence outputs or create a Git commit.
