# Resume here: historical S3/query integration

## 1. Current checkpoint — 2026-11-10 UTC

**Ready to pause. There is no unfinished deployment to wait on.**

| Concern | State |
|---|---|
| AMS | Historical Enrichment POC **0.1.3**, active/latest at live recheck; image remediation unverified |
| Agent ID | `420e63bd-8220-48bd-bada-743f0daea46c` |
| Environment / tenant | ScaleGov staging / platform (`6a1099f9e1ca37ee1216d8c3`) |
| Hosted v3 test | 98 observations / seven incidents → 323 logical query plans; two managed output files |
| Actual AWS searches | **None.** Every planned search was `not_configured`; application status `partial` |
| Local historical search | Implemented and tested against synthetic JSON history |
| Database / SQL | **Not defined or implemented.** Local JSON schema is a test contract, not an AWS table requirement |
| Triage → Enrichment | Automatic handoff implemented by entry, then Recommendation; receiver calls no other agent |
| Donovan | Operator-confirmed full-chain run/five attachments through entry; no downstream discovery tag needed |
| Tests | Last recorded 24 tests: 22 passed, two SDK-only tests skipped; hosted acceptance separately passed |
| Security | Local Semgrep unavailable; package ready=true is not a clean-scan attestation |

Release IDs, input-file identity and hosted evidence: `AMS_RELEASE.md`.
Current workflow: [DEMO.md](../DEMO.md); latest tests/evaluation: [EVALUATION.md](../EVALUATION.md).
Current matching semantics: `HISTORICAL_SEARCH.md`.
Receiver input shape: `AMS_HANDOFF.md`.
Do not assume this last-observed deployment state is permanent; recheck when resuming.

## 2. Decisions already made versus still open

**Keep unless explicitly revised:** deterministic code owns query planning/results;
v3 input, `alert-enrichment/1` output; exact managed-file receipt; no invented
indicators; no public intelligence services; no automatic compromise verdict.
Default lookback is 30 days before each incident start, with current incident
excluded. IP prevalence and activity tuple recurrence are different questions.

**Still open:** AWS schema/format, query engine, field mapping, network scope,
coverage tracking, workload identity, AMS-to-AWS network access, costs/timeouts,
provider SDK dependencies and production result schema extensions.
Partitioned Parquet + Glue + Athena SQL is a candidate, **not a selected design**.
S3 is storage, not an agreed query interface. Do not make the data team use the
fixture's field names or require all history to fit into a local JSON document.

## 3. Ask the data team for this non-secret integration packet

Fill this checklist with actual values and redact sensitive row content. Record
secret reference names only, never keys, session tokens or signed URLs.

### Storage and query engine

- [ ] AWS account/environment and region; data owner/contact.
- [ ] Bucket and permitted prefixes; format/compression; approximate size/growth.
- [ ] Object/partition layout, including time/site/exporter partitions.
- [ ] Chosen query mechanism (Athena/catalog, existing API/database, or another
      explicitly approved mechanism); a bucket alone does not answer this.
- [ ] If Athena: catalog/database/table, workgroup, engine version, partition
      discovery/projection, results prefix, result encryption and lifecycle policy.
- [ ] Versioned schema/DDL and a small redacted sample with expected query answers.
- [ ] Schema evolution policy, null conventions and source record identifiers.

### Meaning of the data

- [ ] Event start/end versus ingestion timestamp; timezone and epoch units.
- [ ] Flow direction/counter semantics; whether timestamps describe interval or event.
- [ ] IPv4/IPv6 representation, protocol representation (e.g. number 6 versus TCP),
      ports, exporter ID and source-site/network/tenant scope.
- [ ] NAT fields, DHCP/address reuse, private address overlap across sites.
- [ ] Duplicate exports, counter updates, aggregation and sampling rates.
- [ ] Retention, collection start/end, ingestion watermark, known gaps/outages and
      authoritative method to prove completeness for a requested interval/scope.
- [ ] Whether DNS/domain, country, ASN and registration labels exist at all, their
      provenance and observation/freshness times. NetFlow alone commonly lacks them.

### Access and operational policy

- [ ] Data markings, permitted processing/export, tenant isolation and retention.
- [ ] Approved AMS workload identity / IAM role and trust mechanism. Local AWS
      credentials do **not** automatically grant a deployed AMS agent AWS access.
- [ ] Source-prefix read permission, catalog permissions and any KMS/Lake Formation
      grants; no source writes/deletes.
- [ ] For Athena, query execution/status/result/cancellation permissions and isolated
      result-prefix read/write access (query results are writes, source stays read-only).
- [ ] Approved AMS egress path, endpoints, DNS/TLS and private networking requirements.
      Verify reachability from AMS, not only an operator laptop.
- [ ] Maximum scanned bytes/cost, duration, concurrency, retry count, per-run budget,
      sample size, result retention and cancellation requirements.

## 4. Agree the mapping before coding SQL

Produce a reviewed mapping with **actual column + type + transform + null behavior
+ event-time meaning + source/quality/coverage** for each supported criterion:

| Logical concept | Current use | Integration decision |
|---|---|---|
| `start`, `end` | Whole-record historical interval containment | Map exact UTC semantics; do not silently change to overlap matching |
| `src`, `dst` | Exact normalized IP in either endpoint | IPv4/IPv6 types and partition-safe predicates |
| `protocol` | Uppercased protocol for activity tuple | Map numeric protocol IDs through explicit supported mapping |
| `src_site` | Exact site for directed activity tuple | Define exporter/network scope; missing mapping must not broaden activity search |
| `dst_domain` | Exact normalized domain, not DNS lookup | Only if independently present and explicitly supplied to consumer |
| `dst_country`, `dst_company` | Exact supplied destination-label prevalence | Label vocabulary/provenance; no ownership or geolocation inference |
| `dst_asn`, `dst_registered_org` | Optional exact attribute prevalence | Only when input and history both support it |
| Record identity | Samples and deduplication | Stable source record reference; not a connection count |
| Coverage/watermark | Controls trustworthy negatives | Scope/field-specific completeness; a successful SQL query alone is not coverage proof |

Current historical interval: `[incident_start - lookback, incident_start)`, with
record start >= lower, start < upper, end <= upper. Boundary-crossing records are
excluded. Confirm this meets the investigation need before changing it.
IP prevalence is currently dataset-wide; private-IP reuse cannot be resolved
without an approved scope policy. A new scoping rule changes semantics and needs
tests and explicit output policy/versioning, not just an invisible SQL filter.

Do not select by model-generated prose. Use fixed, reviewed predicates and bound
values appropriate to the chosen engine. Table/column identifiers come from trusted
allowlisted configuration, never alert strings. SQL syntax/examples should be
written only after the engine and schema are agreed.

## 5. Implementation sequence and exact edit points

1. **Inspect first.** Read scoped `AGENTS.md` and the documents above. Re-run the
   baseline tests and freshness check before edits. Inspect current release state
   via AMS tools after reconnecting through the AMS panel if necessary.
2. **Design the adapter.** `history.py` exposes
   `HistoryAdapter.search(criteria, start, end, sample_limit)` plus `metadata` and
   `errors`. Keep the offline adapter and test vectors. Add a separate live adapter
   with validated configuration, source provenance, field capabilities and coverage.
3. **Plan scale explicitly.** `enrich.py` currently iterates queries synchronously;
   the 323 plans must **not automatically become 323 billable full-table scans**.
   Consider batching/caching/indexed queries and shared scans while preserving
   per-incident windows/criteria, samples and per-query outcomes. Define aggregate
   byte/time budgets before enabling live access. Async/cloud SDK work must not
   block the hosted event loop; select and test an appropriate execution model.
4. **Keep cloud responses normalized.** Preserve the result fields/status semantics
   documented in `HISTORICAL_SEARCH.md`. Timeout, access denial, unsupported field,
   incomplete pagination or coverage gaps must never become a clean negative.
   Record source/query references, coverage, retrieval time and bounded samples;
   never persist tokens, signed links or raw exceptions.
5. **Wire all entry points deliberately.** `ams/hosted.py` currently constructs
   `UnconfiguredAWSHistory()` directly, returns `history_status="not_configured"`
   and prints a fixed AWS-pending status. `enrich.py` also sets
   `capabilities.aws="not_connected"`, while its CLI only offers `--history` or
   `--aws-pending`. These are **code changes**, not just environment configuration.
   Update each to reflect real adapter outcomes; preserve explicit disabled mode.
6. **Dependency and security gate.** Do not hand-edit scaffold requirements or
   assume an AWS SDK exists in the runtime. Resolve a supported packaging and
   scan-compatible transport plan, workload auth and egress with platform owners.
   Never shell out to `aws`, add direct outbound POSTs, or suppress scan findings.
   A GET-only S3 adapter is not automatically feasible for an Athena API workflow.
7. **Stage owned core.** `prepare_pod.py` copies exactly `contracts.py`, `enrich.py`
   and `history.py` into `ams/` and hashes them. Add any new owned adapter modules
   to its explicit staging list. Do not edit staged copies independently. Keep
   production `ams/fixture/` empty and upload/test data outside the source bundle.
8. **Test locally and hosted, then release.** Follow gates below. Publish a new
   semantic version to the existing Enrichment agent ID, not a replacement agent
   or a Triage release. Preserve original 0.1.0 release evidence, but do not restore
   its security-disabled image as a rollback. A rollback
   must be an explicit approved release/lifecycle action; do not assume a tool can
   pin any arbitrary historical version. Record exact version, bundle and test IDs.

## 6. Acceptance gates

### Repeatable local regression

From `enrichment_agent/`:

```sh
python3 -m unittest discover -s tests -v
python3 prepare_pod.py --check
```

After core changes, stage before running freshness-dependent tests:

```sh
python3 prepare_pod.py
python3 -m unittest discover -s tests -v
python3 prepare_pod.py --check
```

Use fresh output directories for CLI examples; existing evidence is not overwritten.
The two skipped SDK tests still need execution in an appropriate managed runtime.
The typed local probe's messages-only input mismatch is documented; use raw
Harness file dispatch for representative hosted acceptance instead of loosening
the receiver schema.

### New adapter tests (no cloud credentials in fixtures)

- [ ] Schema mapping, protocol/IP normalization, null handling, missing columns,
      unavailable metadata and schema changes fail explicitly.
- [ ] Known positive/negative source rows, directed/reversed activity, boundary
      timestamps/timezones, same IP in different sites, IPv6 and NAT policy.
- [ ] Gaps, delayed ingestion and insufficient retention produce unknown/partial,
      never “never seen”; unsupported metadata is explicit.
- [ ] Duplicate records, counter updates, invalid rows and bounded deterministic samples.
- [ ] Pagination completeness, zero results versus failed queries, result decoding.
- [ ] Permission denial, KMS/catalog errors, network failure, timeout, bounded retry,
      query cancellation and scan/cost budget exhaustion.
- [ ] Injection-safe value binding and identifier allowlist; no provider secrets in
      JSON, logs, Markdown, checkpoints or exception text.
- [ ] Batch/cache behavior matches unbatched logical results without cross-user or
      cross-scope leakage. Counts remain record counts, not connections or flows.

### Authorized limited AWS test

- [ ] Start with a small approved prefix/table partition and known expected rows.
- [ ] Compare result counts/sample records/time ranges against a human-reviewed query.
- [ ] Record data snapshot/watermark, query IDs, scanned bytes, elapsed time and budget.
- [ ] Verify from the **deployed AMS runtime** using its approved identity/egress.
- [ ] Confirm actual managed output files retain v3 IDs/references and source-query
      provenance, and status text describes live versus disabled mode correctly.
- [ ] Test same-thread no-file request: no stale attachment reuse.
- [ ] Run packaging/security checks; wait for active version and verify stored output
      channels/file events. Do not equate active deployment with functional AWS access.
- [ ] Document that AWS verification does not itself prove Donovan UI compatibility.

## 7. Integration status and separately authorized future work

- **Triage caller (implemented):** invokes Enrichment only after confirmed creation, using the
  actual exported handoff ID, not `source.input_file_id` (the original findings ID).
  Current stages retain child IDs, verify receipts and preserve partial status;
  no automatic submission retry or distributed exactly-once guarantee.
- **Donovan (entry configured):** entry discovery and full-chain attachments are
  operator-confirmed. Direct downstream listing is unnecessary; markings remain open.
- **Recommendation (implemented):** separate agent consumes `alert-enrichment/1`
  after receipt validation; returns `alert-recommendations/1` and analyst Markdown.
  AWS-pending output remains unavailable history, not historical evidence.
- **Producer v4:** separate reviewed migration if full domain/registration inventory
  is needed; don't extract domains from company names or model hypotheses.

## 8. Copy/paste prompt for the return session

> Resume the Enrichment Agent in enrichment_agent/. Read AGENTS.md, README.md,
> S3_INTEGRATION.md, HISTORICAL_SEARCH.md, AMS_HANDOFF.md and AMS_RELEASE.md first.
> Preserve triage_agent and existing release evidence. Recheck current Enrichment
> state (last checkpoint 0.1.3 active; image fix unverified) and ../DEMO.md.
> Automatic handoffs are implemented; AWS remains disabled. We now have data schema, query engine,
> redacted samples, coverage policy and approved IAM/egress details: [provide these,
> not credentials]. Review the mapping and query-cost plan before implementing the
> live history adapter. Keep logical criteria separate from physical SQL and
> preserve unknown/partial semantics. Implement/test the agreed integration, stage
> core with prepare_pod.py, then request/confirm the desired release scope. Do not
> alter the existing Triage caller or Recommendation agent unless separately requested.
