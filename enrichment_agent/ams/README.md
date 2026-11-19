# Historical Enrichment AMS pod

The source bundle is prepared by `../prepare_pod.py`. It stages the existing
deterministic modules into this directory with byte-for-byte checks, avoiding a
second independently maintained search implementation. Run preparation after any
core change and run its freshness test before packaging. Generated core files
are identified in `core_provenance.json`.

Local source accepts exactly one current-invocation file reference in Harness
`slot="sources"` OR a `slot="triage_handoff"` form containing the v3 object under
`params.handoff`. The structured channel is unpublished. It validates
`alert-indicators/3` and creates the same managed JSON/Markdown outputs.
No local sample data is used. AWS is explicitly `not_configured`.
This receiver invokes no other agent. The entry orchestrates the implemented
Triage → Enrichment → Recommendation sequence.

Text-only, missing and ambiguous inputs fail schema validation; null tasks cannot
reuse prior input. The exact envelope, bounds and canonical receipt are documented
in `../AMS_HANDOFF.md`. Historical full-chain Donovan output is documented in
`../../DEMO.md`. Do not put IDs or JSON into free-text instructions.

Current checkpoint: Historical Enrichment POC 0.1.2, verified active/latest
2026-11-10; image fix remains unverified. See `../AMS_RELEASE.md` and `../S3_INTEGRATION.md` for
the return-session checklist. No cloud query engine or schema is selected yet.
