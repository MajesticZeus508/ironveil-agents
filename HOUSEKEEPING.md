# Documentation cleanup record

## Current documentation pass — 2026-11-18

- Updated root README, operator runbook, evaluation and source inventory to the
  verified 0.1.30 / 0.1.5 / 0.1.9 checkpoint and exact source IDs.
- Consolidated contradictory READMEs: deployed LUX compatibility, both structured
  handoffs, canonical receipt validation and separate export status are current.
- Added [workflow architecture](triage_agent/WORKFLOW.md) with exact graph envelopes,
  canonical-json/1 versus original file/event hash semantics, bounds, checkpoint
  stages, failure controls and source edit points.
- Added [documentation map](triage_agent/DOCUMENTATION.md) to distinguish current
  runbooks/contracts, historical decisions, proposals and immutable evidence.
- Updated scoped maintenance guidance, receiver contracts, S3 resume checkpoint,
  verification headers, Donovan guidance and output index. Older phase records
  retain their evidence, clearly labeled or linked to the current guidance.
- Documented staging's missing sandbox SGP URL configuration: no upload dispatch,
  no confirmed attachments; not a diagnosed storage-backend outage and not proven
  staging-only. Production untested. No credential/host/policy workaround.
- Recorded latest existing SDK results (151 passed, zero skips) separately from
  hosted 1/1 diagnostics and the older 28/35 seven-incident evaluation. No full
  suite rerun, inference or hosted test was needed for this documentation pass.
- Preserved published-source snapshots, staging release trees/provenance, pod
  README bytes, fixture/output bytes and unrelated pre-existing dirty work. No
  file moves/deletions, code change, publish, platform mutation or Git commit.

Validation commands: `python3 -B triage_agent/tests/check_documentation.py` and
`git diff --check`: **55 Markdown documents checked, zero link/fence errors;
diff whitespace check passed**. These checks do not certify anchors, external
links, narrative correctness or deployed behavior.

## Historical cleanup — earlier checkpoint

- Read current agent instructions, operating documents, contracts, reviews,
  release/reliability ledgers and latest performance evaluation.
- Rechecked seven visible staging agents and current network-agent versions.
- Updated team landing page/runbook and agent-level current-state summaries.
- Consolidated test/evaluation presentation in [EVALUATION.md](EVALUATION.md),
  keeping failed runs, skipped tests and measurement limits visible.
- Removed exact duplicated maintenance and session-checkpoint paragraphs.
- Corrected historical preflight/pending/latest wording so it cannot be mistaken
  for an instruction to rerun an already completed benchmark.
- Repaired four **test-only** references to the missing fixture name using the
  existing hash-verified staging input. No production behavior changed.
- Fresh offline regression: **99 discovered, 80 passed, 19 skipped, zero failures**.
  Enrichment staged-core freshness passed. No dependency installations or inference.
- Added repeatable local Markdown link/fence check:
  `python3 -B triage_agent/tests/check_documentation.py`.

## Retention decisions

Keep dated reviews (including Appendix C), design proposals, release/reliability
ledgers and source-backup records: they retain distinct decisions, exact receipts,
failures, provenance and unresolved cautions. Superseded does not mean disposable.
Keep snapshots, staging release source/provenance, diagnostic pods, fixtures and
all generated reports unchanged. Do not rewrite old reports with today's renderer.

The `enrichment_agent/ams/README.md` is part of deployable source. It is deliberately
not edited by documentation cleanup to avoid bundle drift; its earlier checkpoint
is superseded by its parent README and AMS_RELEASE. Source snapshots likewise
retain historical wording.

## Not completed / not claimed

**Full AMS-to-local backup is incomplete.** The inventory identifies two missing
VoF implementations, current-source download/hash-comparison gaps and hosted
output recovery work, with exact source IDs and operator pull commands:
[AMS_INVENTORY.md](AMS_INVENTORY.md).
The available API tool does not save binary downloads; its lossy ZIP text cannot
be used to restore source. No shell credential workaround was attempted.

During this documentation pass: no publish, hotswap, agent restore, metadata/credential change, Git initialization
or commit. No new hosted model test, security scan, semantic-quality audit,
Dev-environment verification or complete archival of all historical AMS versions.

## Documentation review scope

The link/fence checker covers top-level workspace/agent Markdown and Recommendation's
output index. It does not certify external links, Markdown anchor spelling, browser
rendering or generated report semantics. Immutable source snapshots, pod copies
and generated evidence outputs are intentionally outside its rewrite/check scope.
