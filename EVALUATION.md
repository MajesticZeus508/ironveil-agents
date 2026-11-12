# Staging test and evaluation summary

## Executive result

The workflow is functional but **not reliably producing every incident analysis**.
The latest recorded controlled sequence used entry **0.1.24**, Enrichment **0.1.3**
and Recommendation **0.1.4**, the versions independently rechecked in AMS.
All five chains completed orchestration/export; only one produced all seven
validated Recommendation analyses. No new hosted inference was launched for cleanup.

## Hosted evaluation — 2026-11-11 UTC

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

## Fresh offline regression — housekeeping

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
3. Investigate the guarded managed-read/receipt failure without weakening checks.
4. Complete binary-safe source backup and per-file hash comparison.
5. Obtain final-image security evidence before broader data use.
