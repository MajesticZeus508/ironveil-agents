# Alert Triage performance measurements

## Latest three-agent staging evaluation — 2026-11-11 UTC

Entry 0.1.24 / Enrichment 0.1.3 / Recommendation 0.1.4: five sequential runs,
all five stages and five files each; **28/35 validated analyses**, six timeouts,
one validation rejection. Parent median **190.490s**, range **162.103–209.962s**.
Only one run achieved 7/7. See [team summary](../EVALUATION.md) and
[exact five-run ledger](STAGING_PERFORMANCE_2026-11-11.md).

## Historical operator-confirmed three-agent workflow — 2026-11-10

Operator-confirmed parent `inv_b394de1e-5e49-4616-8495-f936041f9844`:
206.181s created-to-completed, 201.110s after start, 5.071s startup/admission.
17 findings / seven groups / 98 observations, five attachments, 7/7 Recommendation
analyses with zero failures. Triage is extraction-only; AWS history not configured;
application partial remains explicit. Batch averages 12.13s/finding and
29.45s/incident are not per-call latency or an SLA. Full stage timings and exact
child IDs: [shared runbook](../DEMO.md). No controlled concurrency speedup claim.

The following standalone model-per-group measurements are historical and are not
like-for-like comparisons with the current three-agent workflow.

## End-to-end release comparisons

Same synthetic fixture: 17 findings, seven grouped analyses, 98 exported
observations. Unless noted otherwise, seconds are invocation created_at through
completed_at, not browser upload/render/download time. These are observations,
not a controlled model comparison or SLA. Argon was used throughout this table.

| Release / design | End-to-end seconds | Context passed/failed | Interpretation |
|---|---:|---:|---|
| 0.1.10 full hosted output | 385.14 | Not established here | Historical baseline; do not assume seven valid contexts |
| 0.1.11 file-first | 275.39 | 3/4 | Seven provider calls; 267.83s total inference spans |
| 0.1.12 reliability fixes | 115.23 | 7/0 | 109.01s after start; successful single run |
| 0.1.14 overlapping run 1 | 309.671 | 6/1 | See full benchmark below |
| 0.1.14 overlapping run 2 | 251.175 | 6/1 | See full benchmark below |
| 0.1.14 overlapping run 3 | 213.308 | 6/1 | See full benchmark below |
| 0.1.15 text progress | 103.339 | 7/0 | 97.065s after start; 19 live updates verified |
| 0.1.16 thinking progress | 287.646 | 5/2 | 281.568s after start; two 90s model timeouts |

Later run evidence:
- 0.1.15: `inv_dfd0e08f-d7fc-4924-bf7b-d74282d743ec`, thread
  `727f29c5-e52a-4a6b-8a61-c0f3110616f8`, export
  `db737e2a-2613-46da-a032-1ca39dcf5440`. Saved SSE/output evidence:
  `outputs/progress_verification_0.1.15.json`.
- 0.1.16: `inv_0ed6c7bf-c868-4f73-b74b-44a15992c0f0`, thread
  `390351f6-d42f-493d-97c7-e80124c1994a`, export
  `4d9933ea-0354-4022-a818-7572219adce6`. External-service and fanout-host
  contexts each hit about 90s. All observations retained; run marked partial.

The presentation change adds no inference calls. Large runtime variance is mostly
inside the sequential model-call path; serving/queue/provider/gateway attribution
is not isolated. Startup/admission was about 5–6s, not the dominant component.
No fresh inference benchmark was run for documentation housekeeping or 0.1.17,
whose downloaded source matches the 0.1.16 implementation.

## Sequential isolated context diagnostic

Production source/deployment unchanged. Local-only pod plugins/triage_isolation
reuses LiveContextClient, prepare_request, validation and original fixture. Same
Argon model, schema constraints, nonstreaming call, 90-second timeout, zero retries.
No overlapping diagnostic requests. Local managed gateway path, not hosted runtime;
these measure the individual context call, not full invocation/export wall time.

| Group | Findings | Observations | Serialized input bytes | Result | Call+validation seconds |
|---|---:|---:|---:|---|---:|
| Nicollet Island | 1 | 10 | 6597 | APITimeoutError, no response | 90.061 |
| External service 197.43.113.112 | 1 | 10 | 6584 | completed, 2 hypotheses / 2 checks validated | 27.108 |

An initial Nicollet diagnostic was also attempted before adding safe structured
stdout reporting; one gateway call occurred but probe returned no reply/result,
so no timing/outcome is claimed for that attempt. The measured retry and comparison
above ran sequentially. Harness probe's graph fault label on the timeout is not
the application diagnosis: diagnostic stdout records the caught APITimeoutError.

Conclusion: timeout reproduces without overlapping benchmark runs. Roughly equal
payload sizes exclude size alone as an explanation. Content/prompt-dependent
provider/gateway behavior is suspected, not proved. No causal field ablation was
performed, so zero_variance/null z-score or a particular source string cannot be
identified as the cause. One pair is not a latency distribution or provider SLA.

## Historical three-run overlapping staging benchmark — v0.1.14

Model: gemini/gemini-4-argon. Same uploaded JSONL-content file for each fresh
conversation: 603b38f6-a61a-4941-a804-121e72330852, 62315 bytes, SHA-256
6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a.
Expected 17 findings, seven incident groups, 98 observations.

Timing: created_at to completed_at measures API submission through persisted agent
completion, including queue/runtime admission, file read, context calls and export.
Does not include initial browser upload, browser rendering or user download.
Calls within a run remain sequential. Three runs launched ~55 seconds apart and
overlap; results are NOT isolated sequential single-user latency measurements.
No source/model/config changes during the benchmark. Each run creates a new export.

| Run | Invocation | Thread | Created UTC | Started UTC | Result |
|---|---|---|---|---|---|
| 1 | inv_d4261ac3-22ee-45db-a199-225314b4369c | be66bd74-e8ac-4889-8be1-52005366e178 | 20:44:09.309371 | 20:44:14.517152 | partial; export created |
| 2 | inv_bf69173d-13f0-428b-91b9-94dfc43c1653 | 9513d7dc-6531-4aa9-8d88-297ae6f7df28 | 20:45:04.765042 | 20:45:10.200367 | partial; export created |
| 3 | inv_1987c2ab-4d4e-4945-a859-6e84878c4fda | 59bd8114-b6f0-4aaa-9009-d20649d35f88 | 20:45:59.737781 | 20:46:05.150867 | partial; export created |

Date: 2026-11-05 (platform timestamps).

## Results

| Run | Completed UTC | End-to-end seconds | After-start seconds | Context completed/failed |
|---|---|---:|---:|---|
| 1 | 20:49:18.980754 | 309.671 | 304.464 | 6/1 |
| 2 | 20:49:15.939968 | 251.175 | 245.740 | 6/1 |
| 3 | 20:49:33.045876 | 213.308 | 207.895 | 6/1 |

Mean end-to-end: 258.051s (4m18s). Median 251.175s. Range 213.308–309.671s.
Admission overhead roughly 5.2–5.4s per run. All three invocations completed at
platform level; all three application runs partial, not fully successful context
generation. Each accepted 17 findings, seven groups, zero input errors, exported
98 observations and confirmed a durable FileBlock. No validation rejections in
these runs. Nicollet Island context timed out in all three: APITimeoutError at
90.012/90.013/90.012s. Six remaining contexts passed in each run (18/21 overall).
All extraction/exports succeeded (3/3); complete seven-context runs 0/3.

Export IDs, run order:
- c4401dfa-166e-46d6-9da8-a965f3b8ff0e
- 276c65e4-72a3-499e-a4b3-e2460a3d2d55
- 4cb8f3a2-c6e1-408c-a348-6774a3419f08

Inference latency/timeout remains a bottleneck. These overlapping observations
cannot establish isolated latency, causal load effects, cold-start behavior, or
reliable percentiles. Do not interpret declining runtimes as a proven cache effect.
