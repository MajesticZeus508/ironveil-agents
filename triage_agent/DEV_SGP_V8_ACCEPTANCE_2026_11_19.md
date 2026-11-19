# Dev SGP v8 write acceptance — 2026-11-19 UTC

Operator authorized file-write testing after the SGP v8 release. Verified profile
`scalegov-dev`, tenant `69dfa4b844ff488d98b2674f`, and active/latest versions:
IronVeil Investigation — Start Here **0.1.31**, Historical Enrichment **0.1.6**,
Recommendations **0.1.10**. This is an AMS API test of IronVeil, not a browser
Donovan Chat invocation or proof of a UI download.

Exactly one fresh LUX-form invocation using `DEV_LUX_INPUT_2026_11_18.json`:

- Invocation: `inv_eedbfd35-2ec2-4369-a249-c8777871fb20`.
- Thread: `fd06d9ee-2e96-4dbe-a94b-3a86557eed62`.
- Actual invoked version: **0.1.31**, platform completed.
- Created `2026-11-19T18:41:19.793765Z`, started `18:41:31.797472Z`, completed
  `18:41:32.995433Z`.
- Output checkpoint: `1f1e448d-7702-6d86-801f-7d671f314b62`.
- One accepted finding, one group, seven observations, zero input errors;
  extraction-only, no Triage model analysis.

## Confirmed managed-file creation and readback

**Triage's managed write succeeded.** `indicator_export.status=created` agrees
with a file block in the run_triage action-scoped OutcomeEvent:

| Field | Value |
|---|---|
| Filename | `extracted_indicators.json` |
| File ID | `0eb654aa-37a1-4861-97be-80b056d48b4e` |
| MIME/schema | `application/json` / `alert-indicators/3` |
| Export-reported byte SHA-256 | `1e8a205afaa99b7c59f059518a73e1dad75fc840f852619969ba1cf0d1829121` |
| SGP metadata size | 5,701 bytes |
| SGP metadata created | `2026-11-19T18:41:32.612000` |
| Metadata MD5 | `a3a00c2fb282703df25c1dd91f0fb28a` |

Read-only `GET /v5/files/{id}` and `/content` on the files service both returned
HTTP 200 in the same Dev tenant. Decoded content contains the expected schema,
one incident and seven observations, synthetic flags, unknown identity and
deferred narrative. The tool returns decoded JSON, so this is successful semantic
readback, **not an independent exact-byte SHA-256 recomputation**. No success HTTP
status is retained in the application export; no numeric upload status is claimed.
No write-failure diagnostic was returned for this successful creation.

## Separate workflow failure limits acceptance

The next tool returned:

```json
{"error":"structured_handoff_unavailable","diagnostics":{"stage":"submit_enrichment","elapsed_seconds":0.0,"retry_policy":"no_submission_retry"}}
```

The preceding durable run_triage output includes `enrichment_handoff.status=ready`,
so this is a separate stage-state/handoff retrieval failure requiring diagnosis.
Local `plugins/alert_triage/stages.py:270–272` emits this error before `submit()`
when the prior tool result's prepared status is not ready. No child invocation
ticket/ID appears in the output. Downstream tools were not reached; **Enrichment
and Recommendation file writes remain untested** by this run. No independent
receiver invocation was launched. The final generic warning that a child may be
running is not evidence that one was submitted.

Final application result: **INVESTIGATION INCOMPLETE**, with one confirmed
attachment retained. This demonstrates that the previous missing-SGP-config
blocker is cleared for this Triage runtime; it does not establish all-five-file
or full-chain success. No retry, resume, republish, source edit, policy change,
credential workaround, staging operation or platform configuration bypass.

## Later separately authorized receiver tests

Direct Enrichment and Recommendations file-mode tests subsequently confirmed all
four downstream exports, each with file blocks and metadata readback. This does
not resolve automatic orchestration. Exact IDs and receipts:
[downstream write verification](DEV_DOWNSTREAM_WRITES_2026_11_19.md).
