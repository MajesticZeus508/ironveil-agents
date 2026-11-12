# Documentation cleanup record

## Completed

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

The `enrichment_agent/ams/README.md` is part of deployable source and retains its
historical 0.1.2 checkpoint. It was deliberately not edited during documentation
cleanup to avoid application-bundle drift; current state is in its parent README
and AMS_RELEASE. Source snapshots likewise retain historical wording.

## Not completed / not claimed

**Full AMS-to-local backup is incomplete.** The inventory identifies two missing
VoF implementations, current-source download/hash-comparison gaps and hosted
output recovery work, with exact source IDs and operator pull commands:
[AMS_INVENTORY.md](AMS_INVENTORY.md).
The available API tool does not save binary downloads; its lossy ZIP text cannot
be used to restore source. No shell credential workaround was attempted.

No publish, hotswap, agent restore, metadata/credential change, Git initialization
or commit. No new hosted model test, security scan, semantic-quality audit,
Dev-environment verification or complete archival of all historical AMS versions.

## Documentation review scope

The link/fence checker covers top-level workspace/agent Markdown and Recommendation's
output index. It does not certify external links, Markdown anchor spelling, browser
rendering or generated report semantics. Immutable source snapshots, pod copies
and generated evidence outputs are intentionally outside its rewrite/check scope.
