# Managed file-write diagnostics

**Published follow-up, 2026-11-18:** diagnostics deployed as Triage 0.1.30,
Enrichment 0.1.5 and Reporting 0.1.9. One hosted chain confirms all three report
`missing_sgp_configuration` / ValueError / request_may_have_been_sent=false.
See [release and diagnosis](DIAGNOSTIC_RELEASE_2026_11_18.md). Added Nov 17 locally,
published Nov 18 with authorization. No historical release/snapshot, dependency
pin, model, credential or platform configuration changed.

Each pod owns a small identical `file_writes.py` adapter (parity tested). It
makes at most one write call and returns either a validated confirmed file ID
or a fixed diagnostic. Triage's `indicator_export.write_diagnostic` and child
`exports[].write_diagnostic` expose failures. Child tool results also include
`export_diagnostics`; Triage projects only allowlisted fields after checking
the child's input receipt. A malformed diagnostic cannot supply arbitrary text.
No report schemas/payload hashes are changed by diagnostics.

Example for the real SDK with no usable runtime base configured:

```json
{
  "operation": "managed_file_write",
  "category": "missing_sgp_configuration",
  "http_status": null,
  "exception_type": "ValueError",
  "request_may_have_been_sent": false,
  "retry_policy": "never_automatically_retry"
}
```

For the actual SGP SDK client, the adapter first resolves its public `base_url`
property with no network I/O. Missing/blank `SGP_API_URL` yields the category
above; a present unusable value yields `invalid_sgp_configuration`. An explicit
valid SDK URL override still works; no fallback or guessed host is introduced.
The local test proves classification behavior; the Nov 18 hosted run separately
confirms this same diagnostic at the deployed boundary in all three agents.

Other categories: `authentication_rejected` (401), `permission_denied` (403),
`rate_limited` (429), `storage_unavailable` (5xx), `http_rejected` (other non-2xx),
`invalid_success_response` (2xx without a valid ID), `request_not_sent` (SDK
explicitly says false), `transport_or_client_failure`, `invalid_write_response`
and `write_exception`. Unknown exception names become `OtherError`.

`request_may_have_been_sent` is tri-state: false only when the SDK/configuration
boundary establishes it; true for an HTTP response or explicit SDK true flag;
null for an ordinary exception/response lacking evidence. **True does not mean
the file was stored.** A timeout or general ValueError during the write is not
misrepresented as definitely unsent. No category enables automatic retries.

No exception text, traceback, response body, arbitrary type name, headers,
URLs, environment values or credentials enter the diagnostic. Confirmed IDs
require integer 2xx status, no failure envelope, a bounded nonblank ID without
control characters. Triage now rejects false-success IDs on non-2xx replies.
Uncertain writes still stop subsequent exports, no ID/attachment is claimed,
and cancellation propagates. Diagnostics are durable tool status, not a new
claim in model prose or the report schema.

## Verification

Installed Agent Kit **0.50.0** runtime (sling-agent 0.1.0 versus unchanged deploy
pin dev6): **91 Triage + 34 Enrichment + 26 Reporting = 151 tests passed, no
skips**. Triage includes nine diagnostic tests exercising all three adapters,
real SDK result envelopes and missing/invalid config without network calls,
401/403/429/503, malformed successes, first/second write failure, cancellation,
unknown exception names, redaction, remote diagnostic projection and copy parity.
Existing structured-chain/checkpoint regressions pass. Enrichment staged-core
freshness passed. These local tests do not require live model/storage calls;
hosted verification and publication are recorded separately in the release ledger.

Agent Kit docs state: “Low-level resource clients return `ResourceOk` or
`ResourceFailure`.” See [resource failure handling](https://scaleapi.github.io/spark-agent-kit/how-to/error-handling/#catch-resource-failures-in-your-own-code)
(0.50.0). Verified result fields against pinned
`v0.50.0:src/spark_agent_kit/_transport/results.py`, URL resolution against
`utils/http.py`, and the call path against `middleware/resources/sgp_client.py`.
No dependency internals were patched.

Authoritative hosted diagnostics were obtained once on Nov 18. Platform owners
must restore matched runtime SGP URL/policy configuration before a separately
approved fresh storage acceptance. Do not overwrite retained releases, guess a
host, copy credentials or retry old unconfirmed writes. Staging is confirmed;
production remains untested, and storage health behind the missing config is unknown.
