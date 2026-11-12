# Dev migration — 2026-11-10

**Polling retry follow-up:** see [bounded polling release evidence](POLLING_RETRIES_2026-11-10.md)
for entry 0.1.25; the migration checkpoint below is retained as history.

Target: ScaleGov Dev, tenant `69dfa4b844ff488d98b2674f`.
Staging records, versions and retained snapshots were not modified.
The working source now targets Dev receivers; do not republish it to staging
without restoring the staging receiver IDs documented in `../DEMO.md`.

| Agent | Dev ID | Version |
|---|---|---|
| Network Investigation Demo | `7f244b84-ff27-43b0-a629-99a76791373a` | 0.1.24 |
| Historical Enrichment POC | `e8dc7ffc-c6d5-4920-9c12-a25e797835d8` | 0.1.2 |
| Recommendation Agent POC | `2cf86942-3a14-40e4-95e5-4a90e752b259` | 0.1.3 |

Entry source changes are limited to downstream agent IDs in `handoff.py` and
`stages.py`. Entry Donovan discovery/upload metadata was copied to Dev.
All three package checks returned ready=true; local Semgrep was unavailable.
Generic local probes rejected messages-only input before inference; the strict
Harness contract was preserved. Downstream hosted Harness missing-file checks
completed with the expected missing_handoff / missing_enrichment replies.
No full-chain file acceptance or image vulnerability remediation is established
by those checks. AWS history remains unavailable; human review is required.

The two VoF agents have not been migrated: their source bundles are not in this
workspace. Platform-default chat agents were not copied or modified.

## Final checkpoint

All three Dev versions reported active/latest. Entry hosted Harness invocation
`inv_f6bb87c3-1acb-4e83-a0b2-3a453b387181` completed and correctly requested an
original findings attachment, without claiming analysis. Downstream checks:
Enrichment `inv_73cbd5a3-6e70-406c-832b-6e9339828c28`; Recommendation
`inv_7859d156-3323-45d5-a248-013a8d20c4b1`.

Offline regression: Triage 44 passed / four skipped; Enrichment 22 passed / two
skipped; Recommendation 14 passed / one skipped. No failures after updating the
Triage test's expected receiver ID to Dev. Enrichment staged-core freshness passed.
SDK-dependent skipped tests and full uploaded-file chain acceptance remain open.
