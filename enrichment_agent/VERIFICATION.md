# Enrichment verification ledger

## Diagnostic release — 2026-11-18

**0.1.5 active/latest**, source c7a914e7-f679-4266-967e-f451bd5bf74a. Hosted
child inv_7169913e-64fc-4d80-8be0-c99f0abf3cc2 completed structured processing;
file write stopped before dispatch: missing_sgp_configuration, ValueError,
request_may_have_been_sent=false. No attachment claimed. Suite 34/34 passed.
See [joint release](../triage_agent/DIAGNOSTIC_RELEASE_2026_11_18.md).

## Historical implementation checkpoint — diagnostics before publication

Added pod-owned `ams/file_writes.py` and per-export/top-level safe diagnostics.
No raw exception/body/header values, no automatic retries or false attachments.
SDK 0.50.0 suite **34/34 passed**; shared adapter/cancellation/redaction/config
tests and five-stage regression in Triage also passed. No deployed update.
See [diagnostic contract](../triage_agent/FILE_WRITE_DIAGNOSTICS.md).

## SDK/full-chain follow-up — 2026-11-17

Installed Agent Kit 0.50.0 runtime executes **34/34 tests, no skips**; core
freshness passes. Full code-owned structured result output added and actual
five-stage SDK/checkpoint chain passed with both intermediate stores failing.
Source uploaded as `bcda0044-ebaf-42ff-87fa-40bcbc761e34`; one 0.1.4 publish
request failed at staging ARP outbound-policy authentication dependency (503).
Read-only reconciliation still shows 0.1.3 active/latest, no 0.1.4. No retry.
Local scan unknown; hosted/storage/Donovan acceptance blocked. Exact details:
[joint ledger](../triage_agent/STRUCTURED_CHAIN_RELEASE_2026_11_17.md).

## Structured receiver — 2026-11-17 (local, unpublished)

Implemented only inside `enrichment_agent/`; no Triage/Recommendation edits,
release, invocation, model call, cloud call or credential setup. Existing
untracked MITRE integration plan left untouched. Triage 0.1.28 still needs a
separately approved caller change; no final-report storage fix is claimed.

- Baseline: 24 discovered, 22 passed, two SDK skips; staged-core check passed.
- Final `python3 -m unittest discover -s tests -v`: **34 discovered, 30 passed,
  four SDK skips**. `python3 prepare_pod.py` staged owned core changes;
  `python3 prepare_pod.py --check` and `git diff --check` passed afterward.
- Executed tests cover explicit-mode ambiguity before I/O, malformed/non-JSON
  values, finite numbers, size/depth/string/node limits, invalid IPs/refs/joins/
  counts, independent repeated/concurrent processing without shared cache,
  canonical hash/snapshot behavior, partial/unknown/provenance preservation,
  uncertain writes without retry and file/form equivalence. Full existing
  handoff equivalence preserves all 98 observations and seven incidents.
- File receipts retain original stored-byte hashes; canonical payload hashes
  match structured mode despite serialization differences. A UTF-8 regression
  checks that the canonical encoding does not tighten the file byte-size limit.
- Added SDK tests for closed form wire roundtrip, mixed/repeated/missing modes,
  prose rejection, null-task rejection, same-state file/form replacement and
  injected tool dispatch. **These are skipped here**, alongside routing/output
  projection tests, because Agent Kit is absent from this CLI interpreter.
  Simulated state replacement and concurrent pure processing are not a real
  checkpointer or hosted thread-isolation acceptance test.
- Read Agent Kit 0.50.0 Forms documentation and pinned source
  `v0.50.0:src/spark_agent_kit/api_contracts/harness/input/{contract,channel}.py`.
  No SDK API, scaffold requirements, model or public output channels changed.
- No new scaffold, `builder_probe`, package check, hosted verification or publish
  was run in this offline edit. The ordinary probe's messages-only input cannot
  exercise this strict Harness receiver. Previous package/hosted results below
  do not certify these new bytes; SDK/checkpoint tests, packaging/security and
  authorized raw-Harness acceptance remain release gates. Publication requires
  explicit approval. No automatic submission/replay or write retry was added.

Exact future caller envelope/hash verification: [AMS_HANDOFF.md](AMS_HANDOFF.md#structured-input-local-unpublished).

## Historical housekeeping result — 0.1.3

Fresh ordinary CLI: **24 tests discovered, 22 passed, two SDK tests skipped**;
`python3 -B prepare_pod.py --check` passed. Python 3.9.6 is below the documented
3.11+ floor; this is not a new managed-runtime certification. No model/cloud calls.
Live staging **0.1.3 active/latest**; five-run hosted evaluation confirms both
exports in each chain, AWS still unavailable. See [team evaluation](../EVALUATION.md).
Current downloaded source snapshots/hosted files are not fully mirrored locally;
see [inventory](../AMS_INVENTORY.md). Historical checkpoints below are retained.

## Historical session-close housekeeping — 2026-11-07

Documentation-only housekeeping added `S3_INTEGRATION.md` and scoped `AGENTS.md`,
linked the return checklist, and corrected stale hosted-verification wording.
The regression suite was rerun: **24 tests, 22 passed, two SDK tests skipped**;
`python3 prepare_pod.py --check` passed. No application code, deployed version,
Triage files, fixture data or saved output evidence changed in this pass.

## AMS receiver follow-up

24 tests ran: 22 passed and two SDK-only tests skipped in the CLI environment.
Managed-file receiver tests confirm exact file reads, v3 validation, provenance,
AWS-pending outcomes, confirmed exports and no retry of uncertain writes.
`builder_check` reports ready=true with no blockers, but no local Semgrep scan.
The graph imported/constructed in the managed probe; the probe's messages-only
input was rejected by the strict Harness contract before execution. End-to-end
hosted verification was pending at that point. Subsequently published 0.1.0 is
active/latest; a hosted v3 handoff prepared 323 AWS-pending queries and created
both managed output files. Stored output/file events and no-stale-attachment
follow-up succeeded. See `AMS_RELEASE.md` for evidence and remaining UI/AWS limits.

## Original offline-core verification

- `python3 -m unittest discover -s tests -v`: **17 tests passed**.
- Final synthetic example: **8 queries**, completed; destination IP appeared in
  two prior records, while the exact directed activity tuple appeared in one.
  The current-window record was correctly excluded.
- `outputs/verified_demo/`: final JSON and Markdown example artifacts.
- Existing triage export compatibility test preserved all **98 observations** and
  **seven incidents**, with original provenance and context.
- The operator-supplied `extracted_indicators (3).json` also parsed and ran against
  synthetic history: **323 queries**, completed. Artifacts are in
  `outputs/uploaded_handoff_compatibility/`. These results demonstrate compatibility,
  not actual historical network coverage.
- AWS-pending CLI produced **five not-configured results**, partial status and
  exit code 2; artifacts are in `outputs/aws_pending/`.

Tests cover historical boundaries, normalization, exact activity versus prevalence,
coverage-dependent negatives, partial positive counts, provenance, duplicate and
conflicting records, malformed inputs, unsupported metadata, upstream context
failure, query identity, untrusted strings, overwrite protection, and sanitized
adapter failures. No AWS connectivity, IAM, Athena/S3 execution or scale benchmark
was verified in the original offline pass. Hosted deployment was subsequently
verified as described above. No triage files were edited.
