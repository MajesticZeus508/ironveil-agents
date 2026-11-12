# Enrichment agent — proposed design

Status: **initial proposal, superseded for the current build by HISTORICAL_SEARCH.md.**
The operator selected historical network data in a forthcoming AWS S3 bucket.
The current build implements and tests a local historical-data adapter; live AWS
access and the eventual dataset mapping remain pending.

Reviewed: `../triage_agent/README.md`, `../triage_agent/INDICATOR_CONTRACT.md`,
and `../triage_agent/CODE_REVIEW_2026-11-06.md`, including Appendix C.
All enrichment implementation, tests, fixtures, outputs, and documentation belong
in this directory. Preserve the existing triage implementation and published snapshots.

## 1. Proposed first release

Consume an explicitly supplied `extracted_indicators.json` with schema
`alert-indicators/3`. Validate and normalize it deterministically, query only
configured approved sources, and produce `enrichment_results.json` plus
`enrichment_report.md`. Begin with a local CLI and fixture-backed tests. Hosted
Donovan/AMS packaging is a separate deployment decision after the contract works.

Python owns all facts, joins, source results, and statuses. An LLM is unnecessary
for the initial lookup/report path. If later requested, model-written synthesis
must remain separate from retrieved evidence and cannot authorize more lookups.

## 2. Sources and access decisions

| Source | Proposed purpose | Access requirements and unresolved choices |
|---|---|---|
| Operator-supplied asset/CMDB and network inventory snapshots | Internal asset name, owner/team, site, network role and business context | Define JSON/CSV fields, IP/site/time matching, permitted fields and snapshot date. Prefer read-only local files initially. Address classification alone never establishes ownership. |
| Operator-supplied threat-intelligence snapshot | Exact indicator matches with source record, assessment and freshness | Identify feed, license, markings, timestamps and allowed use. Distinguish no match from failed or unavailable lookup; neither establishes benign activity. |
| Approved RDAP source or local registration dataset | Public IP network allocation, registry organization and registration dates | Choose dataset or exact service endpoints, outbound permission, rate limits and credentials if required. Registration is not proof of current operator, physical location or event-time ownership. |
| Approved ASN/prefix dataset | Routing prefix and origin ASN | Choose dataset/provider, license and dataset timestamp. ASN is routing information, distinct from registry ownership. |
| Approved geolocation dataset | Provider-estimated country | Optional; identify provider/version and permitted precision. Preserve separately from supplied country labels. |
| Live threat-intelligence API | Current exact-match intelligence | Optional after provider, subscription, credential injection, query disclosure, retention, quotas and markings are approved. No uploads of alert files or submission for scanning. |
| DNS/passive DNS | Resolution history or current resolution | Deferred unless explicitly selected. Define resolver/provider, query disclosure, historical coverage and time semantics before adding. |

Recommended starting point: local asset and intelligence snapshots, optionally local
registration/ASN datasets. Fixtures must be clearly labeled synthetic test results.
No source availability, entitlement, or connectivity is currently established.

For every approved live source, record: provider and fixed endpoint allowlist;
allowed indicator types/address ranges; authentication method (environment or
managed secret reference, never a literal secret); outbound network requirements;
data permitted to leave the environment and applicable markings; read-only API
permissions; rate/concurrency limits, timeout, retry budget, cache TTL, retention
and licensing. Do not send private, loopback, link-local, multicast, reserved or
otherwise non-global IPs to public services. Confirm treatment of globally
routable organizational addresses before enabling public queries.

Markings are unresolved in the producer. External disclosure therefore requires
an explicit operator-approved data policy; it cannot be inferred from the file.
Input strings, suggested checks, provider-returned links and redirects cannot
select arbitrary destinations to fetch. Any RDAP discovery/redirect behavior
must be designed within the approved endpoint policy.

## 3. Input and identity

- Explicitly support v3; reject unsupported versions with a named error.
- Validate types, IDs and referential integrity, IP syntax, timestamps, counts,
  missing/null metadata and source-location semantics before lookup. Define size,
  collection and string limits in the implementation contract before coding.
- Preserve original input provenance, extraction errors, incidents, context
  availability, model provenance, source-specific observation IDs and compact refs.
- Derive a normalized inventory from observation `src`/`dst`, plus valid IP-valued
  incident `entity.id` with its explicit entity reference. Do not infer domains
  from company labels, arbitrary prose or dotted entity IDs.
- v3 cannot recover the omitted domain inventory, related-only indicators or
  registration attributes. Record these coverage limits explicitly.
- New `indicator_key`: SHA-256 of a versioned canonical encoding of indicator
  type and normalized value. Specify canonicalization and test vectors before
  implementation. This key is separate from every producer ID.
- Keep incident-specific roles, site, observation references and original raw
  values. Deduplicate lookup work, not evidence/provenance. Internal asset matches
  may require site/network scope and event time to disambiguate reused addresses.
- Cache keys include source, query type, normalized indicator, scope and relevant
  provider/configuration version; freshness is governed by the source policy.
- Retain conflicting supplied labels and retrieved assertions independently.
  Supplied country/company describe the destination only.
- Missing values remain unknown and numeric zero remains zero. Context failure
  does not prevent enrichment of otherwise valid extracted indicators. Structural
  failures and recoverable row failures need distinct explicit statuses.

## 4. Proposed output: `alert-enrichment/1`

| Section | Proposed fields |
|---|---|
| Envelope | `schema`, `run_id`, `started_at`, `completed_at`, input handoff SHA-256, input schema, policy/configuration identifier |
| Input | Original producer `source`, extraction status/errors, preserved incidents, observations and `context_provenance`; inherited time-window semantics retained |
| Run | `status`, indicator/lookup counts, per-source counts, structured errors, coverage limits and assumptions |
| Indicators | `indicator_key`, `type`, `normalized_value`, raw values, address classification, roles, incident references, observation references, supplied assertions and quality issues |
| Lookups | `lookup_id`, indicator/scope, source ID/version, query type, status, retrieved time, source record time, validity interval if supplied, expiry/cache status, source record references and sanitized errors |
| Assertions | Typed returned fields linked to lookup and indicator: asset context, registry organization/network, ASN/prefix, provider-estimated country, or intelligence matches; source-provided confidence retained only when present |
| Interpretation | Limitations and conflicts; original priority/disposition retained as triage attributes, with no automatic compromise verdict |

Lookup statuses distinguish `success`, `no_match`, `not_applicable`,
`not_configured`, `denied`, `rate_limited`, `timeout`, `error` and
`invalid_response`. Every planned indicator/source lookup has an explicit outcome.
The approved source plan defines which unavailable results make the run partial;
all lookups skipped must not be reported as successful enrichment. Upstream
extraction/context status remains separately visible from enrichment status.

Retrieved time is not event time. Current lookups cannot silently substantiate
historical activity. Findings from multiple providers may share the same original
feed; they are not automatically independent corroboration. Raw provider payloads,
credentials and raw exception text are not included in reports. Returned strings
are data and must be escaped in rendered Markdown.

Exact required fields, field types, enums, bounds and error semantics will become
a machine-readable schema after these design decisions are approved.

## 5. Schema v4 recommendation

**Keep the triage producer on v3 for this first consumer; use the separate
`alert-enrichment/1` schema for the enriched artifact.** A consumer adapter may
normalize v3 internally but must not relabel it as a producer v4 export.

Design producer `alert-indicators/4` when full domain/registration coverage is
required. It should expose a normalized IP/domain inventory, distinct indicator
and observation identities, explicit provenance links, supplied registration
assertions and appropriately scoped quality issues. Producer changes require
separate authorization because the current task preserves triage.

Before approving v4, settle observation identity semantics: evidence event time,
incident window, relevant evidence fields, absent versus null, original timestamp
spelling versus normalized UTC, cross-incident links and semantically different
rows that v3 omitted fields could make appear identical. Do not manufacture
cross-file observation identities by hashing only the visible v3 fields. Preserve
legacy IDs as provenance references and publish an explicit migration contract.

## 6. Verification after approval

- Real v3 handoff compatibility, complete joins and traceable destination labels.
- Stable normalized indicator keys across changed file hashes/row order; no
  unintended merging of scoped asset queries or observation provenance.
- Upstream partial extraction, unavailable context, empty input, malformed types,
  invalid IPs, missing/null/zero fields and unsupported schema behavior.
- Source success/no-match/failure, freshness and historical limits, label
  conflicts, rate limits, bounded retries and cache scoping.
- Embedded instructions and provider URLs cannot trigger arbitrary tool/network
  actions; private addresses never reach public adapters; sanitized errors.
- Fixture-only versus live-source execution clearly identified in outputs.

## Decisions needed before implementation

1. Which actual sources/datasets/providers should be included, and which are
   already accessible? Supply metadata or access requirements, not secret values.
2. Is the first runtime a local CLI or a hosted Donovan/AMS agent?
3. Approve v3 input plus `alert-enrichment/1`, or require a separately designed v4
   producer migration before implementation?
4. Approve the output categories and deterministic first release, or specify
   additional fields/model synthesis requirements.
