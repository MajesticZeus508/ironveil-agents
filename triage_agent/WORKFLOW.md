# Current IronVeil workflow and handoffs

Checkpoint: **2026-11-18**, ScaleGov staging / platform. Entry **0.1.30**,
Enrichment **0.1.5**, Recommendations (also called Reporting) **0.1.9**.
See [release evidence](DIAGNOSTIC_RELEASE_2026_11_18.md),
[operator runbook](../DEMO.md) and [documentation map](DOCUMENTATION.md).
These are last-verified versions, not a promise that latest remains unchanged.

## Architecture

```text
Current explicit findings file OR LUX finding object
  → run_triage: deterministic extraction → alert-indicators/3
  → submit_enrichment: triage_handoff form, one child submission
  → collect_enrichment: verify receipt + full structured_result
  → submit_recommendation: enrichment_handoff form, one child submission
  → collect_recommendation: verify receipt, project confirmed exports/status
  → human analyst (no response actions)
```

The entry orchestrates both children; Enrichment does not invoke Reporting.
Triage makes zero model calls by default (`narrative_deferred`); optional live
context remains available with `TRIAGE_EXTRACTION_ONLY=false`. Enrichment plans
history criteria deterministically with AWS disabled. Reporting uses one Argon
call per incident, concurrency two, with no model retries or fallback.

Each numbered workflow tool runs as a separate checkpoint-sized turn. Tool
results retain code-owned payloads/tickets and status. Public output remains
`messages` and Harness `render_events`; structured transport is not a new
top-level output channel. Payloads can therefore be retained in checkpoint and
tool/event content: synthetic-data, marking and retention restrictions still apply.

## Entry input

Normal Donovan use: upload one findings file, not an intermediate export.
One explicit `sources` file resource, at most 1,000,000 received bytes and 100
records; UTF-8 JSON object, array, `{"findings": [...]}` or JSONL. The preserved
17-finding fixture is `staging_input_verification.json` (JSONL content).

Alternatively an API/event caller supplies one explicit LUX finding object:

```python
{"task": {"intent": "dispatch", "payload": {"parts": [
    {"type": "form", "slot": "lux_event", "params": {"event": finding}}
]}}}
```

Here `finding` is a complete `swoop-ueba-finding/1` object, not a JSON string.
No mixed file/form modes or parsing of pasted prose. Event serialization is
sorted compact JSON with `ensure_ascii=False`, `allow_nan=False`, bounded to
1,000,000 UTF-8 bytes. Its receipt hashes that serialization, **not original
transport bytes**. This is distinct from the internal canonical encoding below.
Agent-side support does not prove a live LUX Events rule is configured.

Reviewed compatibility preserves exact unknown/null synthetic entity identity
and opaque detector/measure/site/company labels. No source IP becomes an inferred
host; unknown units or thresholds are not derived from evidence. See
[LUX compatibility](LUX_COMPATIBILITY_2026_11_16.md) and
[ingestion implementation](LUX_EVENT_INGESTION_IMPLEMENTATION.md) for the bounded
rules and their historical implementation checkpoints.

## Internal submission envelopes

Triage → Enrichment, where `handoff` is the original code-owned v3 object:

```python
{"task": {"intent": "dispatch", "payload": {"parts": [
    {"type": "form", "slot": "triage_handoff", "params": {"handoff": handoff}}
]}}}
```

Triage → Reporting, where `enrichment` is the **full** `alert-enrichment/1`
object, including its embedded `alert-indicators/3` input and upstream receipt:

```python
{"task": {"intent": "dispatch", "payload": {"parts": [
    {"type": "form", "slot": "enrichment_handoff", "params": {"enrichment": enrichment}}
]}}}
```

These are graph inputs. An AMS HTTP invocation body wraps one once under `input`;
the remote graph client receives the graph input itself. No accompanying file
resource, narrative reconstruction, automatic file downgrade or stale-input lookup.
Both receivers also support a directly supplied managed file for explicit file-mode
clients, **exactly one file or one form**, never both. Missing, repeated, mixed,
null-task and prose-only requests fail validation before processing. Both input
state channels are replaced on every accepted receiver dispatch.

Agent Kit 0.50.0 describes forms as: “A form carries typed parameters.”
[Forms documentation](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/#forms).
The exact-one-mode and freshness guards above are application-owned checks, not a
claim about generic SDK defaults. Executable contracts:
`plugins/alert_triage/structured_handoff.py`, `../enrichment_agent/ams/input_contract.py`
and `../recommendation_agent/ams/input_contract.py`.

## Hashes, receipts and forwarding

`canonical-json/1` is SHA-256 over ASCII (equivalently UTF-8) bytes of:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"),
           ensure_ascii=True, allow_nan=False)
```

No newline. **Not RFC 8785**: arrays keep order; all keys, unknown extensions and
original values participate; no numeric, timestamp, Unicode or IP normalization.
`1` and `1.0` can hash differently. The Harness wrapper is not hashed.

Each receiver returns a six-field code-owned `handoff_receipt`:

```json
{
  "schema": "alert-indicators/3",
  "input_mode": "structured",
  "file_id": null,
  "sha256": "CANONICAL_PAYLOAD_SHA256",
  "payload_sha256": "CANONICAL_PAYLOAD_SHA256",
  "canonicalization": "canonical-json/1"
}
```

Reporting's receipt uses schema `alert-enrichment/1`. The entry verifies all six
fields against its submission metadata; missing fields, mismatches and receipt
downgrades fail closed. File-mode `sha256` hashes exact stored bytes and carries
the actual file ID; `payload_sha256` separately hashes the decoded canonical
object. Structured mode has no file bytes, so both digest fields are canonical.
Receipts are integrity checks, not source authentication or exactly-once guarantees.

Enrichment's code-owned `structured_result` contains `status="ready"`,
`schema="alert-enrichment/1"`, `canonicalization="canonical-json/1"`,
`payload_sha256` and the full `payload`. More than 20,000,000 canonical bytes is
explicitly unavailable, never truncated. Before forwarding, the entry recomputes
its hash and checks schema, the embedded upstream receipt and run against the
verified child result. It does not read a managed Enrichment file for structured
runs. Legacy explicit file tickets remain supported for read-only reconciliation.

## Bounds

| Structured transport / processing | Enrichment input | Reporting input |
|---|---:|---:|
| Canonical serialized bytes | 10,000,000 | 20,000,000 |
| Nesting depth (root zero) | 40 | 40 |
| Key/string characters | 10,000 | 10,000 |
| Visited values and object keys | 1,000,000 | 2,000,000 |
| Incidents | 1,000 | 100 |
| Observations | 10,000 | 10,000 |

Reporting additionally bounds historical results to 100,000, per-incident model
packets to 180,000 serialized bytes and each export to 24,000,000 UTF-8 bytes.
Strict built-in JSON types and finite numbers only; no coercion or truncation.
Decoded objects cannot represent duplicate keys: file parsers reject them, while
structured producers/HTTP decoders must reject them before constructing objects.
Semantic schema/join/reference/coverage validation remains mandatory after transport
validation. See [Enrichment contract](../enrichment_agent/AMS_HANDOFF.md) and
[Reporting contract](../recommendation_agent/CONTRACT.md).

## Files, status and failure controls

Intended analyst exports (when storage works):

1. `extracted_indicators.json`
2. `enrichment_results.json`
3. `enrichment_report.md`
4. `recommendation_results.json`
5. `recommendation_report.md`

They are **not internal handoff dependencies**. Each write is attempted at most
once; child export loops stop at first failure. Only validated confirmed IDs with
matching action-scoped FileBlocks become attachments. File creation, incident
analysis, historical search availability and platform completion are separate
statuses. A partial/incomplete run never becomes a successful investigation merely
because the platform says completed. Reporting may return a small inline report;
that is not confirmation of a saved file.

Current staging: all three agents fail URL resolution with
`missing_sgp_configuration`, ValueError, `http_status=null`, and
`request_may_have_been_sent=false`. No upload dispatched or attachment confirmed.
Platform owners need to verify matched SGP policy and runtime URL injection;
healthy laptop publication access does not establish sandbox storage access.
Production is untested. No guessed endpoint, credential injection or custom-policy
bypass. [Diagnostic fields](FILE_WRITE_DIAGNOSTICS.md).

One child submission per stage, fresh client/config/thread; no automatic
submission, inference or file-write retries. Read-only collection GETs retain the
bounded [polling retry policy](POLLING_RETRIES_2026-11-10.md). Submission observation
budget 40s; collection 90s Enrichment / 720s Reporting; HTTP timeout 30s, poll 2s.
Observation timeout does not cancel a child. Reconcile acknowledged IDs before
any deliberate retry; checkpointing is not distributed exactly-once recovery.

No AWS/history access, live intelligence, inferred domains, compromise verdict,
alert closure or autonomous response. Supplied labels and model hypotheses are
unverified. Marking propagation and final-image security attestation remain open.
