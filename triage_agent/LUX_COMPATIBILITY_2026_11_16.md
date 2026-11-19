# LUX detector compatibility follow-up — 2026-11-16

## Diagnosis

Six new visible staging invocations arrived at Triage 0.1.26 between
14:11:52 and 14:11:57 UTC. Each executed `run_triage` and rejected its one
finding with `unsupported detector/measure combination`; no export or child
invocation occurred. Platform completed status represents error handling, not
successful extraction. This is a deterministic agent compatibility gap, not
evidence of a model failure, expired credentials, or downstream permission error.

The earlier implementation accepted only `to AMS egress_volume` / `unknown`.
The new observed labels are four `to AMS site_volume` and two
`to AMS company_spread`, all with measures `unknown` and entity
`{type: "unknown", id: null, site: null}`.

| Invocation | Finding |
|---|---|
| inv_1387c4b6-cfa2-44c1-9d5b-0fb780c43446 | d422faa4-a580-456c-b9a4-f672aa0bd189 |
| inv_436f705a-d87e-4e3f-9405-b8a64c8bf4fe | c4ad245b-7ecb-4434-9a30-ce1afff406f0 |
| inv_3d7a31b5-2200-46c1-94ab-61c69c7db0e0 | ee51483e-fae3-49e0-84f2-e4b948baf475 |
| inv_925b8ccc-44c4-45fd-90a5-f59848196615 | 1aad8418-09fb-4ffc-b21e-02495c4936d1 |
| inv_7228c0ca-910d-4b08-ba94-28bded8d300c | ef0c12d4-f194-40e1-a67f-c5d1b0167c9e |
| inv_08c0d1c3-bed9-420a-9d4f-140b65de382f | 8c504306-efd2-44d4-a77f-22d4bd3c63dc |

All six decoded inputs were inspected and replayed locally. Full representative
site/company payloads were reviewed before selecting rules. Site sample has
multiple source IPs (not one host); company sample has one repeated source IP,
which likewise does not establish entity identity. Their observed values (15 and
14) differ from their ten-row samples and must not be assigned units by inference.
Reduced, explicitly labeled representative excerpts are in
`tests/fixtures/lux_2026_11_16_review.json`; they are not original full payloads or
transport-byte receipts. No received input was bundled into production fixtures.

## Local solution

- Centralize exact opaque-pair recognition in `opaque_lux_metric`.
- Permit exactly the three observed labels with measures `unknown`, only for
  `swoop/valhalla/simulated`. No generic prefix stripping, fuzzy matching or
  unreviewed detector families. Canonical pairs remain strictly validated.
- Use the same recognition for acceptance and `unknown_measure_semantics`
  quality flags so widening compatibility cannot omit downstream warnings.
- Preserve labels, scores, observed values, baselines, original identity and
  source references. No inference of entity, site, active-host counts, company
  counts, threshold, or canonical detector semantics.
- Update optional Triage and Recommendation prompts to cover all observed
  unknown-measure labels. Recommendation's existing validator/report/partial
  handling already supports these unchanged v3 handoffs.

## Verification

Plain CLI: **73 Triage tests: 55 passed, 18 SDK/httpx skips**; **20 Recommendation
tests: 19 passed, one SDK skip**; no failures. Existing legacy coverage remains
17 findings/seven groups/98 observations. New regressions cover exact values,
flags, file/event parity and the real local Triage → unconfigured-history
Enrichment → stub Recommendation pipeline for site/company cases.

Read-only fetching of all six full original AMS invocation inputs followed by
local deterministic replay produced **6 accepted findings, 60 observations,
zero input errors**, preserving original entity and observed metrics. No hosted
invocation or resubmission was made. SDK checks were not rerun in a managed
environment in this pass; no SDK code or dependencies changed.

## Deployment and producer follow-up

This is an **unpublished local fix**. Publish separately approved staging
versions of Triage and Recommendation (prompt change), explicitly retaining
**IronVeil Investigation — Start Here** and **IronVeil Recommendations** and
their existing agent IDs. Preserve release snapshots and staging receiver IDs.
Validate with one new synthetic event before considering deliberate replay.

Producer-side durable resolution: send explicit entity type/id/site when known,
stable detector identifier separately from its display label, and explicit
measure meaning/units. Retain unknowns when genuinely unknown. Producer engineers
must confirm these mappings; evidence is not a substitute for that contract.

Only six new Triage runs are visible under the current API identity. The other
four of the ten reported alerts require Events action/invocation reconciliation;
this parser diagnosis does not explain missing deliveries. No rule, permission,
credential, agent name or deployed source was changed in this follow-up.
