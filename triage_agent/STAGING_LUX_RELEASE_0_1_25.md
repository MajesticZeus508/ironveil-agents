# Staging LUX ingestion release 0.1.25

User approved staging publication. Agent: `d4ffbfc9-696f-4a5a-b174-75daaa1c993f`.
Environment: `scalegov-staging`; tenant `6a1099f9e1ca37ee1216d8c3`.

Prepared `releases/staging_0_1_25/` using `tests/prepare_staging_release.py`.
18 deployable files; per-file source/release SHA-256 receipts are in
`releases/staging_0_1_25.provenance.json`. Only the expected three receiver-ID
occurrences differ from editable Dev source. Original 0.1.24 snapshot preserved.

Staging Enrichment: `420e63bd-8220-48bd-bada-743f0daea46c`.
Staging Recommendation: `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f`.

Managed verification before packaging: 67 Triage + 15 Recommendation tests passed,
zero skips; see `LUX_EVENT_INGESTION_IMPLEMENTATION.md` for scope and limitations.
Package check ready=true, zero blockers; local Semgrep scan unavailable/unknown.

Published source file ID: `a2c5f52c-fa35-48b2-9309-cad36ca55602`.
Publication request accepted for version 0.1.25. Initial deployment status pending;
0.1.24 still active/latest. This record does not yet claim hosted acceptance.

Spark rule was NOT changed. It still needs the structured form mapping documented
in `LUX_EVENT_INGESTION_IMPLEMENTATION.md` after deployment readiness is verified.
