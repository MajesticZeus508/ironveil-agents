# Staging LUX compatibility release 0.1.26

Operator approved publication of Triage and Recommendation updates on 2026-11-13.
Environment: scalegov-staging; tenant `6a1099f9e1ca37ee1216d8c3` (platform).

| Agent | Existing ID | Requested version | Display name |
|---|---|---|---|
| Triage entry | `d4ffbfc9-696f-4a5a-b174-75daaa1c993f` | 0.1.26 | IronVeil Investigation — Start Here |
| Recommendation | `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f` | 0.1.5 | IronVeil Recommendations |

Triage was incorrectly named `triage_agent/releases/staging_0_1_25` in live AMS.
Explicit display_name and description were supplied on both publish requests;
subsequent GETs confirmed both intended names. Triage's existing Donovan discovery
tag and upload metadata remained intact. No separate metadata mutation needed.

Prepared `releases/staging_0_1_26/` with the existing staging preparation script:
18 runtime files, empty fixture, only three downstream receiver-ID replacements
versus editable Dev source. Per-file source/release hashes are recorded outside
the pod in `releases/staging_0_1_26.provenance.json`. Prior snapshots preserved.
Enrichment remains unchanged at existing staging ID
`420e63bd-8220-48bd-bada-743f0daea46c`.

Local managed verification: 72 Triage + 19 Recommendation tests passed, no skips.
Both package checks ready=true, zero blockers; Semgrep unavailable/scan unknown.
Argon catalog request-shape check passed. No dependency pins changed.

Published source IDs:
- Triage: `5c17c6e0-e4e0-440e-b7b0-6843b4a17c73`
- Recommendation: `3cc45f20-b79d-4613-af90-b8a8648d2a4b`

Both publication requests accepted. Initial status pending; previous versions
remain active/latest until deployment completes. Hosted acceptance not yet claimed.
No Spark rule change, credential change, Enrichment publication or Git commit.

Exact-version inspection: both reached **Building Image**, step 3/5, after source
download/extraction. Deployment IDs: Triage
`e219ca61-5746-4292-8a33-99b40549590e`; Recommendation
`2bc66a4a-8436-4cbb-82a0-5732247adbbc`. No deployment failure reported at that check.

## Deployment and smoke verification

Both versions subsequently became **active/latest**, confirmed through version
status and parent agent GETs. Parent names remain exactly as listed above.

- Triage 0.1.26 missing-input smoke: completed invocation
  `inv_7ed396e6-2a30-446a-87ef-9a0c046419b9`, thread
  `65c941fd-c1cd-47dc-b5ed-2d6abb5472a2`; explicit input/extraction failure,
  no analysis claimed.
- Recommendation 0.1.5 missing-input smoke: completed invocation
  `inv_41b67249-f64d-408a-b4d8-7fac781aabfa`, thread
  `4c0cb38b-08ed-406e-b7e5-dcc764464f1a`; `missing_enrichment`, no stale upload.
- Direct structured synthetic payload acceptance submitted once to Triage 0.1.26:
  `inv_4a25b574-f9bd-4bce-a764-896f2ff6b960`, thread
  `257f6c0b-9edd-43b1-9839-bd2376db85ef`; running at initial observation.
  This is a direct AMS acceptance test, not a new LUX producer/Events rule delivery.
  No automatic resubmission.

## Structured payload hosted result

Stored output subsequently shows all five stages finished: **one accepted finding,
one group, seven observations, zero input errors, 1/1 Recommendation analyses
completed, five confirmed attachments**. Payload hash matches the original captured
receipt. Enrichment remains AWS `not_configured`; application status correctly
remains partial. No actions executed.

Recommendation child `inv_43e2a174-ab01-4137-bfbc-79bd55fefade` completed on **0.1.5**,
thread `4568da9c-6653-4c11-bc5d-714e2e6761a0`. Enrichment child:
`inv_00195eba-3e7b-4e41-adb5-2745a5614101`.

| Confirmed output | File ID |
|---|---|
| extracted_indicators.json | `28abe33a-8185-40a3-ab43-9e3ffec77884` |
| enrichment_results.json | `52057907-b3f5-4d57-ae72-1dc5bdf1ed55` |
| enrichment_report.md | `3b0f27dc-cf42-4235-aa94-4d82a9f1b09a` |
| recommendation_results.json | `8b0e7acc-453e-4dc0-a461-db6d4c1ae53f` |
| recommendation_report.md | `0c6c10c2-3811-49c8-9d1e-9a10804b948b` |

Inspected child inline report: code-owned unresolved-identity and unknown-measure
warnings present; model calls the IP a source lead and recommends identity checks.
Semantic caveat: model also calls supplied rows “flows” without flow-ID semantics
and describes destination labels as external/cloud infrastructure. Structural
validation is not semantic certification; those interpretations require review.
No deterministic identity filling was introduced. Full exported JSON bytes were
not independently downloaded in this pass. Actual LUX → Events delivery after
release remains distinct from this successful direct structured AMS acceptance.
