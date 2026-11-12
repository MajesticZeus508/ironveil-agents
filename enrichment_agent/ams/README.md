# Historical Enrichment AMS pod

The source bundle is prepared by `../prepare_pod.py`. It stages the existing
deterministic modules into this directory with byte-for-byte checks, avoiding a
second independently maintained search implementation. Run preparation after any
core change and run its freshness test before packaging. Generated core files
are identified in `core_provenance.json`.

Production mode accepts exactly one current-invocation file reference in Harness
`slot="sources"`, validates `alert-indicators/3` and creates managed JSON/Markdown
outputs. No local sample data is used. AWS is explicitly `not_configured`.
This receiver invokes no other agent. The entry orchestrates the implemented
Triage → Enrichment → Recommendation sequence.

Text-only requests return a missing-file error. The receiver contract supports
programmatic file-resource dispatch. Operator-confirmed full-chain Donovan output
is documented in `../../DEMO.md`. Do not put IDs into free-text instructions.

Current checkpoint: Historical Enrichment POC 0.1.2, verified active/latest
2026-11-10; image fix remains unverified. See `../AMS_RELEASE.md` and `../S3_INTEGRATION.md` for
the return-session checklist. No cloud query engine or schema is selected yet.
