# Historical NetFlow search contract

## Scope and decisions for the offline build

The operator selected historical network data in a forthcoming S3 bucket as the
enrichment source. Build a deterministic local CLI with an interchangeable
history adapter now. No live AWS connection is configured or simulated as live.
All code and artifacts stay in `enrichment_agent/`; triage remains unchanged.

Input is `alert-indicators/3`; output is `alert-enrichment/1`. No producer v4 is
introduced. V3 supplies source/destination IPs, protocol, destination country and
company labels, source site, incident windows and provenance. It omits the full
domain and registration inventory. Optional separately supplied
`enrichment-context/1` metadata can provide explicit destination domain, ASN and
registered organization linked to a v3 observation ID. These assertions are
operator-supplied, unverified context, never recovered or invented triage facts.
No DNS, geolocation, WHOIS, threat-intelligence or model calls are made.

## What “seen before” means

Each incident has its own historical interval `[incident_start - lookback_days,
incident_start)`, UTC; default lookback is 30 days, configurable 1–3650 days.
Historical records are eligible only when their entire interval is contained in
that range (`start >= lower`, `start < upper`, `end <= upper`). Records crossing
either boundary are excluded. The current incident and future records are excluded.

Two result categories are deliberately separate:

1. **Indicator prevalence:** exact normalized IP in either endpoint; exact domain
   in `dst_domain`; exact country/company/registered-organization label or integer
   destination ASN. Attribute matches mean that label appeared, not that the same
   endpoint or behavior did. Company/org matching is case-sensitive with whitespace
   retained; country is not silently interpreted as ISO or physical location.
2. **Activity tuple recurrence:** same directed `src`, `dst`, case-normalized
   protocol and exact `src_site`. All four are required. This does not reproduce
   detector behavior, fanout, byte-volume anomalies, connection success or intent.
   Ports are unavailable in v3. No similarity score or compromise verdict is made.

Site scopes activity matches; IP prevalence is dataset-wide and explicitly cannot
disambiguate private IP reuse across sites, NAT, DHCP or address reassignment.

## Local dataset: `historical-netflow/1`

One JSON object with `schema`, `dataset_id`, `synthetic` (boolean), `coverage`,
`fields` and `records`. `coverage` has timezone-aware `start`, `end` and a boolean
`complete`: an operator assertion that collection is complete for that interval.
Do not infer coverage from the earliest/latest returned record. This manifest is
for small fixtures/exported subsets, not a bulk-S3 ingestion format.

Required fields on every record: `record_id`, `start`, `end`, `src`, `dst`.
`fields` lists available searchable fields from `src`, `dst`, `protocol`,
`src_site`, `dst_domain`, `dst_country`, `dst_company`, `dst_asn`,
`dst_registered_org`, plus optional `bytes_sent`, `bytes_received`.
Every declared field must be present and non-null on every valid record. A
dataset with sparse metadata should be split/mapped explicitly or use an adapter
that reports field-specific completeness; it must not declare false completeness.
Undeclared fields are rejected. Protocol strings are uppercased, IPs normalized,
domains use lowercase IDNA with one trailing dot removed. ASN is an integer
1–4294967295; byte values are nonnegative integers, never boolean.

Duplicate identical record IDs count once. Conflicting record IDs are quarantined
in full and reported. Different IDs may describe overlapping traffic; record
counts are not unique connections. Invalid records are reported and excluded.
Returned records retain record ID and local record index; source adapter identity
and input hashes identify the dataset. No byte totals are asserted.

## Result contract

The output preserves the input handoff once under `input`, with its SHA-256,
upstream extraction/context statuses, original IDs, references, nulls and zeros.
Optional metadata is preserved separately. `source` states dataset ID/hash,
synthetic flag, coverage and searchable fields, or `not_configured` for AWS.

Each query result contains:
- Incident ID, observation links, query kind and normalized criteria.
- Content-derived query ID (versioned canonical sorted compact JSON SHA-256).
- IP indicator key where applicable (type plus normalized value, independent of
  source file/incident/provenance).
- Requested time interval and matching semantics.
- `status`: `seen`, `no_match_in_covered_history`, `unknown`,
  `unsupported`, `not_configured` or `insufficient_input`.
  Adapter execution failure returns `error` with a sanitized code.
- `search_complete`, dataset validation errors, matched-record count,
  first/last match times, bounded sample record references and truncation flag.

`seen` requires at least one actual matching historical record, even if coverage
is incomplete; counts are lower bounds when `search_complete=false`. A negative
answer requires full declared coverage, available fields and no invalid or
conflicting records. Otherwise zero matches means `unknown`. Unsupported fields
and absent input are explicit. No matches never means “never seen” or “benign.”
History failures, incomplete searches, missing activity inputs or partial upstream
extraction make run status `partial`; absent optional metadata is reported in
capabilities and does not prevent IP searches. Empty plans have status `empty`.
Upstream narrative failure remains visible but does not invalidate extracted facts.

## Bounds and validation

Stdlib-only Python 3.11+. Input handoff/context limit 10 MB each; history limit
50 MB and 100,000 records; at most 10,000 observations, 1,000 incidents and
100,000 planned queries. Strings at most 10,000 characters, nesting at most 40.
Duplicate JSON keys and nonfinite numbers are rejected. Invalid envelopes/joins
fail before lookup; malformed historical rows are excluded with explicit errors.
Samples are limited to 1–100 (default 5). Reports escape untrusted Markdown/HTML;
no alert text or returned metadata is evaluated as instructions or fetched URLs.

## AWS boundary — pending actual bucket/data contract

`HistoryAdapter.search(criteria, start, end, sample_limit)` is the integration
boundary. A deliberately unconfigured AWS adapter produces `not_configured`.
It makes no network calls and is not a working S3/Athena connector.

Recommended deployment design to evaluate with the data team: partitioned Parquet
in S3, Glue table and bounded Athena queries, rather than downloading the entire
bucket for every indicator. Confirm actual storage, catalog and query service
before implementing that adapter. Batch queries where possible while preserving
per-incident intervals, coverage and per-query outcomes. Define partition pruning,
scan budget, timeout/cancellation, pagination and exact timestamp semantics.

Needed from the data team:
- AWS region, bucket/prefix, table/catalog or object layout and redacted sample rows.
- Field mapping for event start/end, addresses, direction, protocol, ports, site,
  DNS and destination labels; NetFlow commonly lacks domain/registration fields.
- Timestamp units/timezone, sampling, exporter IDs, duplicate/counter semantics,
  NAT and private address scope, retention and collection gaps/watermarks.
- Workload identity (IAM role/profile, no pasted static keys), read-only source
  access, encryption/KMS and Lake Formation requirements if applicable.
- If Athena is selected: workgroup/catalog/database/table, query execution and
  results permissions, isolated results prefix with write/read access, encryption,
  bytes-scanned budget and retention. Source data remains read-only even though
  the query engine writes result files.

Live field mapping, IAM policy and integration tests await those decisions. The
offline tests establish matching/coverage semantics, not AWS connectivity or
large-scale performance. Domain/registration coverage can later justify a
separately authorized producer v4; this build does not modify triage.
