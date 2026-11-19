# Structured chain completion and blocked release — 2026-11-17

## Operator-requested retry: deployed and hosted handoffs verified

On explicit request to try again, reconciled that neither new receiver version
existed and reused the exact uploaded bundles. One fresh publish per receiver
was accepted; both became active. Published Triage only after receiver readiness:

| Agent | Active tested version | Source file |
|---|---|---|
| Enrichment | 0.1.4 | bcda0044-ebaf-42ff-87fa-40bcbc761e34 |
| Reporting | 0.1.8 | 30f2a1dc-34cb-4ff2-ae3b-c04557a29d1b |
| Triage | 0.1.29 | 3631d6b2-7cef-41d1-8fbb-a5afd2db8437 |

Names/descriptions/metadata preserved. Original ARP error did not recur.
Raw Harness hosted receiver checks completed:
- Enrichment: `inv_f1c95a37-bdc7-423d-9322-0a054045a186`.
- Reporting: `inv_2c73bec8-2b98-4475-80b2-178ccdd92e71`, 1/1 model analysis completed.

Full LUX chain:
- Parent `inv_89d6dccf-b716-416c-8fb0-5947d6fcbda5`, thread
  `359345d3-815b-4be9-b3d2-d8136a8ba242`, Triage 0.1.29.
- Enrichment child `inv_934abc18-4c96-4661-b1f5-6fed17943ad3`.
- Reporting child `inv_cc7f3262-4cdb-4670-92b5-548cf651bbc9`.
- All five stages completed; both child submission attempts exactly one;
  Reporting 1/1 analyses completed, zero failures, application partial.
- Recomputed Triage payload hash matches Enrichment receipt:
  `cf4081b27bca2a47fe86c7aaecc6a646a4082c6952ac46ab3e60b0036efca9d8`.
- Recomputed Enrichment output hash matches Reporting receipt:
  `32f235d7287450c7d0aa005fc523c30bb7a708190e9302a31bd5ccc9b9c27d73`.
- Exact enriched `input` equals the original Triage handoff snapshot. AWS history
  unavailable; human review/no-action boundaries retained.

**Report storage remains broken/unconfirmed:** Triage's write was unconfirmed;
Enrichment and Reporting each stopped after their first unconfirmed JSON write,
without retries or fabricated attachments. 0/2 confirmed files for both children.
Parent correctly returned INVESTIGATION INCOMPLETE despite successful handoffs
and 1/1 analysis. No final file IDs exist to verify/download, and Donovan file
rendering cannot be accepted. The file-service exception text is intentionally
not retained, so the underlying storage error is not diagnosed by this evidence.

Evidence: `HOSTED_STRUCTURED_{enrichment_0.1.4,recommendation_0.1.8,triage_0.1.29}.json`
and `STRUCTURED_RELEASE_*.json`. Following sections preserve the initial failed
attempt and local verification history; their blocked-version statements are
superseded by this retry record.

User authorized completing all remaining integration, verification, publication
and hosted acceptance work autonomously. This record supersedes earlier
receiver-only/unpublished implementation descriptions where explicitly noted.

## Implemented

- Triage sends the code-owned v3 object through `triage_handoff` and validates
  the exact child's canonical receipt; the intermediate Triage file write is
  independent and attempted at most once.
- Enrichment's code-owned `run_enrichment` tool result now carries
  `structured_result = {status: ready, schema: alert-enrichment/1,
  canonicalization: canonical-json/1, payload_sha256: ..., payload: ...}`.
  `payload` is the same complete enriched object serialized into its JSON file,
  including the upstream receipt. The hash excludes the wrapper, uses sorted
  compact ASCII JSON/no newline, and includes every field of the payload.
  Payloads over 20,000,000 canonical bytes return an explicit unavailable
  structured result; no truncation. Existing public channels remain messages
  and render_events: the structured result is code-owned tool content.
- Triage verifies that output hash, schema, input receipt and run agreement
  before forwarding through Reporting's `enrichment_handoff` form under
  `params.enrichment`. It never reads an intermediate file for the structured
  route and never automatically downgrades to a file route. Legacy file tickets
  remain supported solely for explicit legacy/reconciliation paths.
- Reporting's full six-field canonical receipt is verified before its exports
  are trusted. Confirmed attachments still require action-scoped FileBlocks.
  The five-stage flow, deadlines, bounded read-only GET retries, unknown history,
  provenance/nulls/partial status, fixed model/prompt and zero response actions
  remain. No additive submission/write retry or crash-safe exactly-once claim.

## Local verification

Found installed Slingshot Python at
`/Applications/Slingshot.app/Contents/Resources/runtime/venv/bin/python`:
Python 3.13.14, Agent Kit **0.50.0**, sling-agent **0.1.0**, LangGraph 1.2.7,
LangChain 1.3.11. Deployed scaffold pins remain unchanged (sling-agent dev6);
this installed-runtime difference remains a hosted acceptance consideration.

- Enrichment SDK suite: **34/34 passed**, no skips.
- Reporting SDK suite: **26/26 passed**, no skips.
- Triage SDK suite before the added full-chain test: **81/81 passed**, no skips.
- Final complete Triage suite: **82/82 passed**, no skips, 436.902s. A combined
  run initially exposed test-only OpenAI HTTP-client cache/type interference;
  moved the transport-method stub after graph construction, then the complete
  suite passed. Production HTTP/model code was not changed for that test fix.
- Added actual SDK/InMemorySaver five-stage chain with real Enrichment and
  Reporting implementations and stub transport/model/stores: **passed**.
  Both intermediate writes deliberately throw; Reporting still receives the
  complete result, finishes one stub narrative, and returns its two exports.
  Checks null identity, unavailable history, partial status, zero actions,
  receipt verification, fresh child configs, text-only reused-thread rejection,
  and hash-tampered output stopping before Reporting on a separate thread.
  This is not a hosted storage test or browser-rendering check.
- Core freshness check passed. No dependencies changed in production pods.

## Target mapping and package preparation

Active profile: ScaleGov **staging**, tenant platform
`6a1099f9e1ca37ee1216d8c3`. Existing agent names/descriptions/metadata were read
and retained explicitly in both publication attempts.

| Role | Agent ID | Existing active/latest | Intended new version |
|---|---|---|---|
| Enrichment | 420e63bd-8220-48bd-bada-743f0daea46c | 0.1.3 | 0.1.4 |
| Reporting / Recommendation | 934ba6f7-3dcc-4dfb-9454-acdc92f7a10f | 0.1.7 | 0.1.8 |
| Triage entry | d4ffbfc9-696f-4a5a-b174-75daaa1c993f | 0.1.28 | 0.1.29 |

Prepared a new isolated `releases/staging_0_1_29/` and adjacent provenance with
the existing script; only downstream ID occurrences differ from editable Dev
source. Old snapshots are intact and editable Dev targets remain unchanged.
Official `pack_pod` checks passed for all three bundles (prepared Triage has
21 archive entries); archive/source hashes
are in the two `STRUCTURED_RELEASE_*.json` evidence records. No uploaded alerts,
fixtures or credentials are bundled.

Local security scan remains **unknown**: the packaged scanner's vendored rules
path is missing. Installed Semgrep 1.185.0 in an isolated temporary environment,
then attempted the actual MCPx checkout rules without modifying/suppressing any
rule; the Semgrep executable was killed (exit -9) before JSON output. This is
not a clean-scan attestation. Server-side scan was never reached because
publication failed earlier at platform policy resolution.

## Publication blocked — no retries

The existing SGP upload forward on 8085 timed out. A new temporary Teleport
forward to the same authorized sgp-api-staging service on 18085 worked; no
profile or credential changes were made. Source uploads succeeded:

- Enrichment source `bcda0044-ebaf-42ff-87fa-40bcbc761e34`.
- Reporting source `30f2a1dc-34cb-4ff2-ae3b-c04557a29d1b`.

The temporary 18085 forward was stopped after publication was blocked; existing
forwards and profile settings were left intact.

Each receiver received exactly **one** publish request. Both returned HTTP 500
`failed to publish agent version` during outbound-policy pinning; ARP returned
503 **Authentication dependency unavailable**. Policy names:
`platform-artifacts-runtime-http-v5` (Enrichment) and
`platform-litellm-runtime-tls-v1` (Reporting).

Read-only version reconciliation found no intended new version; existing
0.1.3/0.1.7 remained active/latest. No retry, identity/policy bypass, hotswap,
credential rotation or alternative deployment was attempted. Triage publication
was deliberately not submitted before compatible receivers exist.

## Remaining external gates

1. Restore staging ARP authentication dependency; reconcile the exact uploaded
   source IDs and versions before a deliberate new publish attempt.
2. Publish/activate compatible receivers, verify raw Harness structured input,
   then publish the prepared Triage staging caller, keeping existing names/tags.
3. Hosted full-chain LUX and file-input acceptance; check original values and
   each payload hash/receipt, one submission per stage, separate child IDs,
   and same-thread missing-input behavior.
4. Independently download/check actual final files and inspect durable
   action-scoped attachments; manually confirm Donovan rendering if browser
   access is available. **Final-report storage is not verified fixed.**

No fresh hosted invocation was launched against incompatible old receivers.
No Git commit or upstream platform change was made.
