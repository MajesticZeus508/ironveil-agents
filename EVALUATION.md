# Staging test and evaluation summary

## Executive result

Latest releases: entry **0.1.30**, Enrichment **0.1.5**, Recommendation/Reporting
**0.1.9** (staging/platform, 2026-11-18). Both structured handoffs work without
intermediate files, but **managed exports are currently blocked**. A single LUX
diagnostic chain completed 1/1 incident analysis with no confirmed attachments.
The older seven-incident evaluation below still shows incomplete narrative
reliability; the smaller test does not supersede its failure rate. No new hosted
inference or full agent-suite rerun was launched for documentation housekeeping.

## Latest hosted diagnostic chain — 2026-11-18 UTC

Parent `inv_7ae33958-b73c-4260-a837-c63b3ba8cf6f`: 18:59:45.356433Z to
19:00:45.596401Z (**60.240s** creation-to-completion, one finding/incident and
seven observations; not comparable to the older 17-finding benchmark).
Both children platform-completed on the exact releases above, one submission
each. Canonical receipts/output hash matched; Reporting 1/1 completed, zero failed.
All 23 history criteria `not_configured`, no AWS searches or actions.

All three writes stopped before dispatch: `missing_sgp_configuration`, ValueError,
HTTP status null, request_may_have_been_sent=false. No confirmed files/readback.
Immediate cause: missing/blank sandbox SGP URL configuration; not evidence of a
storage HTTP outage. Staging confirmed; production untested. Final status correctly
INVESTIGATION INCOMPLETE. [Exact evidence](triage_agent/DIAGNOSTIC_RELEASE_2026_11_18.md).

## Latest full local SDK regression — 2026-11-18

| Suite | Passed | Skipped | Failures/errors |
|---|---:|---:|---:|
| Triage | 91 | 0 | 0 |
| Enrichment | 34 | 0 | 0 |
| Reporting | 26 | 0 | 0 |
| **Total** | **151** | **0** | **0** |

Python 3.13.14, Agent Kit 0.50.0, local sling-agent 0.1.0 (deploy pin unchanged
0.1.0.dev6). Real SDK/checkpointer workflow uses injected stores and stub incident
inference; these are not real storage/model acceptance tests. Includes both form
boundaries, canonical receipts, unknown/null/provenance preservation, fail-closed
validation, independent inputs and nine cross-pod safe-write diagnostic tests.
Enrichment staged-core freshness passed. Three package checks ready=true, no
blockers; local Semgrep unavailable, **security scan unknown**.

## Historical five-run hosted evaluation — 2026-11-11 UTC

Versions 0.1.24 / 0.1.3 / 0.1.4, prior file-based handoffs. Files succeeded then;
that success does not establish storage availability for the current releases.

Same synthetic input, fresh sequential threads, unchanged configuration:
17 findings → seven incidents → 98 observations. Exactly five parent and ten
child submissions; all reconciled platform-completed in the retained ledger.

| Run | End-to-end seconds | Recommendation passed | Failed | Confirmed files |
|---|---:|---:|---:|---:|
| 1 | 201.879 | 4 | 3 | 5 |
| 2 | 171.151 | 6 | 1 | 5 |
| 3 | 209.962 | 5 | 2 | 5 |
| 4 | 162.103 | 7 | 0 | 5 |
| 5 | 190.490 | 6 | 1 | 5 |
| **Total** | — | **28 / 35 (80%)** | **7** | **25** |

- Parent min/median/max: **162.103 / 190.490 / 209.962s**.
- Recommendation active min/median/max: **137.260 / 163.427 / 184.144s**.
- Six timeouts; one validation rejection (subcode not yet recovered).
- All five retained exact receipts, zero input errors and zero polling retries/errors.
- All five application statuses `partial`: expected unavailable history/deferred
  Triage narrative, plus incident failures in four runs. No response actions.

Canonical [five-run ledger](triage_agent/STAGING_PERFORMANCE_2026-11-11.md)
retains exact invocation/thread/file IDs, timing definitions and trace caveats.
[Recommendation interpretation](recommendation_agent/PERFORMANCE_2026-11-11.md)
separates semaphore wait from client-call spans. Neither is pure provider latency.
Run 5 parent and Recommendation status/timestamps and parent stored output were
independently reread during cleanup: 6/7 analyses, both receipts and five file
blocks agree with the ledger. Other runs are retained recorded evidence, not
fresh full-content audits in this pass.

### Earlier release acceptance (not included in the five-run sample)

Entry 0.1.24's first acceptance stopped before Recommendation with
`enrichment_json_unavailable_or_unverified`; three upstream files survived.
The next operator-requested test completed 7/7 in **143.886s**, five files.
The earlier 0.1.23 Donovan success was **206.181s**, also 7/7. Preserve these as
separate observations, not substitutes for the five-run failure rate. The guarded
handoff failure's root cause remains unresolved.
See [release ledger](triage_agent/STAGING_RELEASE_2026-11-10.md).

## Historical ordinary-CLI regression — earlier housekeeping

Command per agent: `python3 -B -m unittest discover -s tests -v`.
Ordinary CLI is **Python 3.9.6**, below the documented 3.11+ support floor;
Agent Kit/httpx are absent. Results are compatibility observations, not a supported
managed-runtime certification. No dependencies installed and no live model calls.

| Suite | Discovered | Passed | Skipped | Failures/errors |
|---|---:|---:|---:|---:|
| Triage | 60 | 44 | 16 | 0 |
| Enrichment | 24 | 22 | 2 | 0 |
| Recommendation | 15 | 14 | 1 | 0 |
| **Total** | **99** | **80** | **19** | **0** |

Triage's initial run failed because the documented fixture name was absent.
The existing `staging_input_verification.json` was independently checked:
**62,315 bytes**, SHA-256
`6b205b4b32e8bb2807a3a98292ff8dd9b49183d2ef201b17175b22a201290a4a`.
Tests now explicitly use that preserved file; the fixture-coverage test also pins
its hash. No deployed code or fixture bytes changed. SDK/httpx skips remain visible.
Enrichment `python3 -B prepare_pod.py --check` passed.

Prior managed verification recorded **60 Triage + 15 Recommendation tests passed,
zero skips**, plus a mocked five-stage/checkpointer run with five file blocks.
That is historical managed evidence, not a new managed rerun or hosted fault test.
Local tests exercise editable Dev-targeted Triage; staging release provenance is
recorded separately. Enrichment's two SDK checks remain unexecuted in this CLI.

## What is not established

- A latency/reliability SLA, causal Dev/staging comparison or concurrency speedup.
- Semantic correctness of every narrative, adversarial robustness or safe closure.
- Live AWS search, coverage-based negatives, current threat intelligence.
- A clean image-security scan, classification propagation or exactly-once recovery.
- Complete downloaded AMS source/output coverage; see [backup gaps](AMS_INVENTORY.md).

## Recommended next steps (not executed)

1. Recover original hosted JSON files without rerunning inference; extract the
   validation subcode and per-incident durations/statuses.
2. Correlate timeout windows with platform-owned gateway/provider timing.
3. Have platform owners restore staging SGP runtime configuration; then authorize
   a fresh synthetic attachment/readback acceptance without weakening checks.
   The older guarded managed-read failure is a distinct unresolved observation;
   structured handoffs remove that dependency but do not retrospectively diagnose it.
4. Complete binary-safe source backup and per-file hash comparison.
5. Obtain final-image security evidence before broader data use.
