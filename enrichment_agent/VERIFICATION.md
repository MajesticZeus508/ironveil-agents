# Enrichment verification ledger

## Current housekeeping result

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
