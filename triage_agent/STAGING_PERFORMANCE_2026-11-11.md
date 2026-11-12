# Five sequential hosted staging tests — 2026-11-11 UTC

## Team summary

**Five complete chains, 25 attachments, 28/35 validated analyses (80%).** Six
timeouts and one validation rejection; only run 4 achieved 7/7. Median parent
time **190.490s** (162.103–209.962s). All application runs `partial`; no actions.
[Team evaluation](../EVALUATION.md) separates fresh offline tests from recorded
hosted evidence. Cleanup independently reread run 5 parent/Recommendation status
and parent output; no replacement inference was launched.

## Protocol and input verification

Operator authorized exactly five new sequential AMS hosted invocations and their
inference costs. Each uses a fresh parent thread and the identical strict Harness
dispatch/resource input. No source, prompts, models, concurrency, timeouts,
deployment settings, metadata or downstream configuration changes are authorized
or performed. Polling uses read-only GETs, never reinvocation. Failures count;
children must be reconciled before the next parent is submitted.

Confirmed `scalegov-staging`, platform tenant `6a1099f9e1ca37ee1216d8c3`.
Pre-test active/latest versions: entry `d4ffbfc9-696f-4a5a-b174-75daaa1c993f`
0.1.24; Enrichment `420e63bd-8220-48bd-bada-743f0daea46c` 0.1.3;
Recommendation `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f` 0.1.4.
All three parent records report compromised=false, takedown_at=null. These fields
and functional tests do not independently attest libexpat1 remediation.

Original staging input remains file `61827a37-3cb1-4a13-8445-cdf1e5ad8ded`.
Direct metadata/content GETs returned 200; metadata filename
`ueba_findings_sim_run2_2026-11-03.json`, size 62,315 bytes. The operator downloaded
this exact upload to `staging_input_verification.json`; read-only hashing returned
SHA-256 `6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`
and 62,315 bytes, matching the required input. No upload substitution was made.
The earlier metadata MD5 discrepancy is not a content SHA-256 mismatch; downloaded
bytes resolve the input gate. See the retained [preflight record](STAGING_PERFORMANCE_PREFLIGHT_2026-11-10.md).

Task text: “Run the network investigation and produce analyst recommendations.”
Graph input has one top-level `task`, intent `dispatch`, text part followed by
`resource` / slot `sources` / file ID above. No explicit model override.

## Completed invocation ledger

### Run 1

- Submitted once: parent `inv_aa5f909f-7445-4440-a033-e7976e057957`, thread
  `40fab5c2-3e0d-488c-bbcc-5bdc5355f03a`, entry 0.1.24.
- Created `2026-11-11T02:23:21.222438Z`; started `02:23:26.792814Z`.
- Recommendation observed running: `inv_17dbe5cd-bd9a-475f-b0e0-ca27dbb5f822`,
  thread `0dce56c2-82e4-4778-997c-e391c12f27e9`, version 0.1.4;
  created `02:23:41.460004Z`, started `02:23:46.654731Z`.
- All three invocations terminal/completed before run 2 submission.
- Parent completed `02:26:43.101457Z`: total **201.879s**, startup 5.570s,
  active 196.309s. Recommendation completed `02:26:40.922107Z`:
  total 179.462s, active 174.267s.
- Enrichment `inv_7d2b50b9-7bfb-4fe6-a014-a35714bdafc0`, thread
  `6b45d654-6d74-410c-8a2f-65557efe8f01`, version 0.1.3; created
  `02:23:30.689520Z`, started `02:23:36.029924Z`, completed `02:23:38.838794Z`:
  total 8.149s, active 2.809s.
- Stages (seconds): Triage 2.118; Enrichment submit 6.400 / collect 4.233;
  Recommendation submit 6.481 / collect 175.450. All stages reached.
- Poll diagnostics: Enrichment 4 GETs, Recommendation 86 GETs; both zero retries,
  empty error categories, stop_category=returned. Each child submission attempts=1.
- Input confirmed by hosted extraction: SHA-256 exactly as above, JSONL,
  17 accepted findings, seven incidents, 98 observations, zero input errors.
- Recommendation 4 succeeded / 3 failed. Saved Markdown independently confirms
  two `timeout` errors and one `validation_rejected`; no claim yet about its exact
  validation subcode. Application partial; all stages finished, not stopped early.
- Both exact file/hash receipts accepted by parent and all five distinct,
  action-scoped FileBlocks confirmed. Files:
  - Triage `443010ca-32f6-4827-afea-e6b128182dfc`
  - Enrichment JSON `dd2d052a-50df-4bfa-a95d-ad0ca1fa1795`
  - Enrichment Markdown `cf7217ff-d7e1-45db-aed2-d2cd90656a89`
  - Recommendation JSON `e6701a27-bb7b-4b1f-b376-492508d6464b`
  - Recommendation Markdown `ddbbd3df-0d42-4273-a5d1-1576c4d3b210`
- Triage receipt SHA-256 `7a1e8d1ef211225c9cbc4bf0b1ec68c9c740d63c28eb31fa1d162747badfae79`;
  Recommendation input receipt `b3552ffafd499d5762f0b5f0a3e13d30d01ae4cb356f0d1a4df31da8a655d373`.
- Direct spans schema returned an empty vocabulary, but a correlated ChatOpenAI
  search did return spans. First observed call span `9d89944f4c5f3469`:
  `02:23:47.698408Z`–`02:24:19.485683Z`, 31.787s client-call duration.
  Schema emptiness therefore is not proof of unavailable traces. Full search
  payload was tool-truncated; no full-trace dump is saved in this report.

### Run 2

- Submitted once after run 1 parent/children reconciled: parent
  `inv_1212b8b0-7703-41bf-9496-d7552a0fe9d0`, thread
  `7999cc3b-cdb3-4afb-b0fd-3321ec20d432`, entry 0.1.24.
- Created `2026-11-11T02:27:05.632433Z`, started `02:27:10.359385Z`.
- Recommendation ticket observed: `inv_804c6a1f-ef64-42f4-953a-3ae9c29bbb54`,
  thread `aa1fde9f-975b-4cbe-af41-41c745cb2866`.
- All parent/child invocations completed before run 3 submission.
- Parent completed `02:29:56.783527Z`: total **171.151s**, startup 4.727s,
  active 166.424s. Recommendation version 0.1.4, created `02:27:23.013732Z`,
  started `02:27:28.323169Z`, completed `02:29:55.874233Z`:
  total 152.861s, active 147.551s.
- Enrichment `inv_f471cc58-331c-4de7-82e5-363603a79b3c`, thread
  `f8723ae8-1350-4a53-8799-770497d908a3`, version 0.1.3;
  created `02:27:12.293004Z`, started `02:27:17.526463Z`, completed
  `02:27:20.338209Z`: total 8.045s, active 2.812s.
- Stages (seconds): Triage 1.034; Enrichment submit 6.051 / collect 4.192;
  Recommendation submit 6.511 / collect 147.526. All stages reached.
- Enrichment/Recommendation GET counts 4/73; zero retries, empty error lists,
  stop_category=returned. One submission attempt for each child.
- Same expected input hash, 17 accepted findings, seven incidents, 98 observations,
  zero input errors. Recommendation **6 succeeded / 1 failed**; independent saved
  Markdown confirms `timeout` for 192.168.213.37. Application partial; all stages finished.
- Both exact file/hash receipts accepted and five action-scoped attachments:
  - Triage `48507f8b-a428-4c5c-9a99-7a0e4f05225d`
  - Enrichment JSON `70e5def7-cfca-4f1a-99d4-9bc81d602372`
  - Enrichment Markdown `c53ef38b-0133-4e69-9295-4a400c704b9e`
  - Recommendation JSON `4b9f1cfb-4713-4909-a97b-59fa1dbd39b3`
  - Recommendation Markdown `8d52b341-6d3f-4876-899f-4f8d72f36848`
- Triage receipt matches run 1 SHA-256; Recommendation input SHA-256
  `f2813507ac0df41e1143be88f12e14a5332d390da50fe5ef1adca5639fe44263`.

### Run 3

- Submitted once, fresh parent `inv_19a2afa4-87c9-4836-977e-3dfde3a6703e`,
  thread `211d02c6-0dc7-4f67-9f67-aea6c304fe33`.
- Entry 0.1.24; created `2026-11-11T02:30:22.993190Z`, started
  `02:30:28.420529Z`. Recommendation observed `inv_05b82df3-6608-4794-b2cd-46c6209e6b00`,
  thread `798fdc67-eaf7-4cd8-b1ea-653f04dd01ae`.
- Parent completed `02:33:52.955211Z`: total **209.962s**, startup 5.427s,
  active 204.535s. Both children reconciled completed before run 4 submission.
- Recommendation completed `02:33:51.474701Z`: total 189.167s, active 184.144s.
  Enrichment total 8.232s, active 2.971s (timestamps below).
- Stages: Triage 1.741s; Enrichment submit/collect 6.141s/4.265s;
  Recommendation submit/collect 6.501s/184.547s. All five reached.
- Collection GET counts 4/90; zero retries/errors, stop_category=returned.
  Child submission attempts each one. Same hash/17 findings/7 groups/98 observations,
  zero input errors. Recommendation **5 succeeded / 2 failed**; fixed categories
  pending independent report read. Application partial, all stages finished.
- Exact receipts verified and five action-scoped attachments:
  - Triage `5077b39b-f2c8-4681-a6d4-508afa1800d7`
  - Enrichment JSON `3fbf1d40-56d5-4f78-80ea-a007670464f9`
  - Enrichment Markdown `18f7293c-37fb-4775-9bdf-8b8c11738578`
  - Recommendation JSON `20e29720-ed28-4df5-aa4a-eed1d41be77d`
  - Recommendation Markdown `8d1c6651-0e0b-4562-8864-ce22f16ffe1c`
- Triage receipt SHA-256 matches previous runs; Recommendation input SHA-256
  `e7acc635c688003c618eed5a124a212397ed4bd6372e698d8eb7076c80ef680b`.

### Run 4

- Submitted once after run 3 parent/children completed:
  `inv_6427b347-a8b5-4ec5-a026-3a35d8f452cf`, thread
  `6ceb1f5b-f60d-4eb1-90e7-c6d8cab32ad1`.
- All three invocations reconciled completed before run 5 submission.
- Parent completed `02:36:53.517116Z`: total **162.103s**, startup 5.200s,
  active 156.904s. Recommendation completed `02:36:52.846204Z`:
  total 143.587s, active 137.260s; created `02:34:29.259181Z`, started
  `02:34:35.586459Z`, version 0.1.4.
- Enrichment version 0.1.3, created `02:34:18.495585Z`, started
  `02:34:23.838179Z`, completed `02:34:27.108642Z`:
  total 8.613s, active 3.270s.
- Stages: Triage 1.026s; Enrichment submit/collect 6.123s/4.162s;
  Recommendation submit/collect 7.516s/137.065s. All stages reached.
- Collection GET counts 4/68, zero retries/errors, stop_category=returned;
  each child submitted once. Expected source hash and 17/7/98 extraction counts.
- Recommendation **7 succeeded / 0 failed**, both exact receipts verified,
  five action-scoped attachments confirmed. Application partial solely retains
  upstream limitations (AWS unavailable/deferred narrative), not incident failures.
- Files:
  - Triage `e98eede6-4596-48cb-83da-92dde1b57d9e`
  - Enrichment JSON `2ee87ba6-dea7-4cd7-bcc6-e6391bd80c15`
  - Enrichment Markdown `f2dbc0fd-5d34-49f6-9090-0161b04fd87c`
  - Recommendation JSON `4e8fcf66-58d5-40a9-8879-b950645c5a65`
  - Recommendation Markdown `13466a7c-fee8-41b1-81ec-98dce4303d8f`
- Triage SHA-256 matches prior runs; Recommendation input receipt
  `c8b4e6aca624b90fe34f674830f922685ae265b69b68f268d228b60e027d95fb`.
- Entry 0.1.24 created `2026-11-11T02:34:11.413893Z`, started `02:34:16.613421Z`.
- Observed Enrichment `inv_b0efd44d-599c-4ad1-9e82-cfa76a2d082d`, thread
  `df9bb43c-009a-4165-95d6-f932e478a7e5`; Recommendation
  `inv_de207604-09aa-42f5-96c0-8162c3bc3d71`, thread
  `d8dc0df2-04a8-4e77-9426-ec727830fbd2`.

## Final five-run timing table

| Run | Parent total s | Startup s | Parent active s | Enrichment total/active s | Recommendation total/active s | Analyses success/fail | Files |
|---|---:|---:|---:|---|---|---|---:|
| 1 | 201.879 | 5.570 | 196.309 | 8.149 / 2.809 | 179.462 / 174.267 | 4 / 3 | 5 |
| 2 | 171.151 | 4.727 | 166.424 | 8.045 / 2.812 | 152.861 / 147.551 | 6 / 1 | 5 |
| 3 | 209.962 | 5.427 | 204.535 | 8.232 / 2.971 | 189.167 / 184.144 | 5 / 2 | 5 |
| 4 | 162.103 | 5.200 | 156.904 | 8.613 / 3.270 | 143.587 / 137.260 | 7 / 0 | 5 |
| 5 | 190.490 | 5.610 | 184.880 | 8.256 / 2.745 | 168.745 / 163.427 | 6 / 1 | 5 |

Run 3 children observed: Enrichment `inv_700c2a86-8cde-4a21-9064-0a0d07c2ae67`,
thread `d4823a11-d6a6-43d4-aa76-74a3d9254da9`, version 0.1.3, created
`02:30:31.201678Z`, started `02:30:36.463146Z`, completed `02:30:39.433874Z`.
Recommendation version 0.1.4, created `02:30:42.307846Z`, started
`02:30:47.330345Z`; completed `02:33:51.474701Z`.

### Run 5

Exactly once after run 4 reconciliation: parent
`inv_065c10ad-e045-446c-910a-f8b0f3a30ddb`, fresh thread
`e58462c7-9f34-4197-b5d7-88dc501c3076`. Parent and both children now terminal/completed.
This is the fifth submission; do not launch another benchmark run.

Entry 0.1.24 created `2026-11-11T02:37:21.016284Z`, started `02:37:26.626576Z`.
Enrichment `inv_4aac425c-68e9-4b1b-9521-24ed764584e2`, thread
`4e48f8d2-48d7-4f01-80df-49bfbc078952`, version 0.1.3; created
`02:37:29.275819Z`, started `02:37:34.787729Z`, completed `02:37:37.532279Z`.
Recommendation `inv_2f51f643-f1f5-4915-8f72-e01ebc758e9b`, thread
`450942b0-551d-4952-a615-c617de842c73`, version 0.1.4; created
`02:37:40.428594Z`, started `02:37:45.746040Z`.

Parent completed `02:40:31.506396Z`; Recommendation completed `02:40:29.173345Z`.
All five stages reached: Triage 1.529s; Enrichment submit/collect 6.418s/4.261s;
Recommendation submit/collect 6.601s/164.907s. Collection GET counts 4/81, zero
retries/errors, stop_category=returned; child submission attempts each one.
Expected hash/17 findings/7 incidents/98 observations and zero input errors.
Recommendation 6 succeeded / 1 failed; saved Markdown confirms `timeout` for
192.168.213.37. Both exact receipts and five action-scoped attachments confirmed:

- Triage `e948f081-1b79-47e3-9074-c6357671b5f3`
- Enrichment JSON `029ea408-9ebc-4e64-886b-bc447889dd3f`
- Enrichment Markdown `ae10776b-f6cd-430c-ad67-f3812fe35015`
- Recommendation JSON `b76ce03e-8bfc-483f-9d85-34a3a9970fce`
- Recommendation Markdown `1effb0a0-f8cc-472a-83af-d7130a042fa9`

Triage receipt SHA-256 matches all prior runs. Recommendation input receipt
`ef13dbebac7ebb9772bcb870646fc44e1f61a7d94a19ad87b5373154fe56f8b8`.
Application partial; stages finished, not an early-stop investigation.

## Final counts and descriptive statistics

Exactly five parent submissions, ten child submissions, all 15 invocations
reconciled platform-completed. Five of five chains reached every stage, verified
both receipts and confirmed five distinct attachments each (25 total).
No unsuccessful run was replaced. Four of five runs had incident-analysis failures;
one of five achieved 7/7. Across 35 attempted incident analyses: **28 succeeded,
seven failed: six timeout, one validation_rejected**. No polling error/retry,
submission uncertainty, export failure or guarded handoff failure was observed.
All five application runs remain partial due to upstream limitations, with
additional incident failures in four runs. No response actions executed.

| Metric (seconds) | n | Min | Median | Max |
|---|---:|---:|---:|---:|
| Parent creation-to-completion | 5 | 162.103 | 190.490 | 209.962 |
| Parent startup/admission | 5 | 4.727 | 5.427 | 5.610 |
| Parent active | 5 | 156.904 | 184.880 | 204.535 |
| Enrichment creation-to-completion | 5 | 8.045 | 8.232 | 8.613 |
| Enrichment active | 5 | 2.745 | 2.812 | 3.270 |
| Recommendation creation-to-completion | 5 | 143.587 | 168.745 | 189.167 |
| Recommendation active | 5 | 137.260 | 163.427 | 184.144 |

These include all five complete chains, including failed incident outcomes; they
are not success-only latency estimates. The fully successful subset has n=1:
parent 162.103s, Recommendation active 137.260s. No meaningful success-only
distribution is established.

Relative to the existing 143.886s staging baseline, median total is +46.604s
(+32.39%); even the fastest test is +18.217s. Baseline 7/7 success contrasts with
only run 4 achieving 7/7 in this sample. This is temporal exploratory variation,
not evidence of a release regression or an environment comparison.

Versions observed in every actual invocation: entry 0.1.24, Enrichment 0.1.3,
Recommendation 0.1.4. Final live status checks retain those active/latest versions;
no deployment-version drift was observed. Model provenance was Argon; no changes
or additional benchmarks were made.

Run 1 direct-files correlated ChatOpenAI metrics: seven spans, client-call
min 25.565s / mean 48.249s / max 90.011s; total overlapping span time 337.745s.
This is not wall-clock runtime and excludes semaphore wait before call entry.
Quantile metrics are approximate (reported p50 31.744s, p90 89.600s). Span status
and metrics are not used to infer failure counts; those come from saved reports.
Saved Recommendation JSON/text reads are accessible but the tool truncates large
payloads before incident-level diagnostics; full per-incident timing extraction
is not yet established. Arbitrary content offset/limit query parameters did not
provide pagination and are not relied on.

Run 2: seven client-call spans, min 25.402s / mean 41.098s / max 90.048s;
approximate p50 30.976s. Baseline: seven spans, min 24.845s / mean 30.588s /
max 41.231s, approximate p50 28.288s. This supports a long-tail call-time
contribution in runs 1–2, alongside saved timeout outcomes, not a measured split
between provider execution, gateway queueing and network latency.

Run 3 terminal direct trace metrics: seven client-call spans, min 24.476s /
mean 51.561s / max 90.039s, approximate p50 47.104s. Saved Markdown confirms
both failed incidents are `timeout` (192.168.213.37 and 192.168.194.160).
Across the first three completed runs, five timeout outcomes and one validation
rejection are confirmed. This is separate from expected upstream partial status.

Run 4 terminal metrics: seven spans, min 23.863s / mean 37.126s /
max 58.495s; approximate p50 38.400s. Successful calls still vary substantially:
the fully successful run 4 is slower than the baseline, without a timeout.

Run 5 terminal metrics: seven client-call spans, min 23.751s / mean 43.701s /
max 90.044s, approximate p50 27.520s. All five runs have seven correlated model
spans, consistent with one call per incident and no model retries. Error counts
are taken from application output, never metric error_count.

## Supported explanations and unresolved questions

- The same input produced the same extraction counts/hash in all five reconciled
  parents. No changes to actual versions have been observed.
- Enrichment active duration is tightly clustered (2.745–3.270s); parent startup
  is 4.727–5.610s. Recommendation active duration varies 137.260–184.144s and
  accounts for most parent timing differences. Read-only polling retries are
  zero throughout, so retries did not cause the observed variation.
- Seven calls at concurrency two cause queue waiting. A slow or timed-out call
  occupies a slot and delays later incidents. Client-call trace timing excludes
  that application semaphore wait; saved incident timing includes it.
- Observed 90s tails coincide with timeout outcomes in runs 1–3, but those tails
  do not distinguish inference serving queue, provider generation or network
  response delay. No rate-limit or capacity claim is established.
- The validation rejection is an analysis-quality/contract outcome, separate from
  transport timeouts. Its subcode is not visible in the truncated JSON tool read.
- The known guarded `enrichment_json_unavailable_or_unverified` failure has not
  recurred in the five tests; this does not prove it fixed.
- Generated Enrichment JSON hashes differ because each run has fresh receipts
  and timestamps. Same original input is controlled, not byte-identical generated
  model packets, cache state, service load or response lengths.

## Recommended next experiments (not executed)

Recommendation-specific findings are cross-linked in
[Recommendation performance notes](../recommendation_agent/PERFORMANCE_2026-11-11.md).

1. Obtain complete saved JSON via a full-byte download path, then extract only
   incident ID, analysis status/error, validation_code, elapsed seconds and stage.
   Preserve original generated artifacts and do not issue replacement inferences.
2. Correlate timed-out client spans with platform-owned LiteLLM/egress/provider
   timing for the exact invocation windows. Request queue/connection/first-byte
   timings, not raw prompts, provider exception bodies or credentials.
3. If separately authorized, run a controlled incident-level paired experiment
   varying packet compaction or concurrency one/two, preserving evidence and
   validation. Do not change multiple factors together; record token counts and
   cache behavior. Neither longer timeouts nor retries are assumed a remedy.
4. Investigate the known managed-byte-read/receipt guard failure separately with
   sanitized failure-stage diagnostics; never bypass integrity checks.

## Interpretation boundaries

AMS timings exclude Donovan browser upload/render/download. Application partial
status is expected for unavailable AWS history and deferred upstream narrative,
even when every Recommendation analysis succeeds. Platform completion is not
analysis success. Argon is configured for concurrency two, one call per incident,
zero model retries/fallback. Per-incident analysis_duration_seconds includes
semaphore queue waiting and must not be labeled pure inference latency or summed
as wall-clock runtime. Read-only polling retries do not fix inference failures.
Five runs are exploratory evidence, not a reliability SLA. The earlier 17-incident
Dev dataset is not an environment-performance comparator.

Comparison baseline (not counted among the five): parent
`inv_cbd08334-b349-435f-8ca1-789b23c55660`, Recommendation
`inv_ba2c8125-1521-4e0b-baa7-fe87484e30ff`; total 143.886s, parent active
138.225s; Recommendation total 122.021s/active 116.606s; 7/7 analyses,
five attachments, zero polling retries/errors. Baseline stages: Triage 1.903s,
Enrichment submit/collect 6.065s/4.205s, Recommendation submit/collect
6.851s/117.404s.
