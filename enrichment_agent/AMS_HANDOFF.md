# AMS receiver and sequential handoff

**Current checkpoint (2026-11-18): Enrichment 0.1.5 active/latest.** The receiver returns a full
`structured_result` in code-owned `run_enrichment` content, independently of
managed write confirmation. Its envelope contains `status="ready"`,
`schema="alert-enrichment/1"`, `canonicalization="canonical-json/1"`,
`payload_sha256`, and `payload` (the exact full object exported to JSON).
Canonical size above 20,000,000 bytes makes it explicitly unavailable, never
truncated. Triage validates the output hash/upstream receipt and forwards through
Reporting's structured form. Public top-level channels remain unchanged.
The local SDK chain and hosted chain passed both handoffs despite intermediate
file-write failures. Initial ARP publication failure was resolved by an authorized
retry, then diagnostics released in 0.1.5 identified missing staging SGP URL
configuration before upload dispatch. No confirmed attachments. See
[latest evidence](../triage_agent/DIAGNOSTIC_RELEASE_2026_11_18.md).

Current staging checkpoint: Enrichment **0.1.5**; automatic structured
Triage → Enrichment → Recommendation verified in hosted acceptance.
The entry owns submission/collection, receipt checks and attachment projection.
See [current runbook](../DEMO.md). Original receiver verification below is historical.

## Implemented now

- Separate pod source in `ams/`, scaffold-owned pins: Agent Kit 0.50.0,
  sling-agent 0.1.0.dev6 and ripgrep-bin 15.2.0.
- Deterministic file-or-form processing, no model inference required for lookup
  planning or status. The scaffold's configured model is `openai/gpt-5.4`; the
  gateway accepted its streaming/system/tool request shape.
- Strict Harness dispatch with exactly one explicit managed file in `sources`
  or the structured form below. Valid requests
  replace both input-state channels; missing/ambiguous requests are rejected.
- Reads exact stored bytes through `SGPResourceClient`, validates v3 and retains
  the received file ID and content hash. No filename lookup, filesystem paths,
  free-text file-ID extraction, stale upload fallback or production test fixture.
- Exports JSON and Markdown through managed file access; only confirmed creations
  become FileBlocks. Uncertain writes are not retried automatically.
- AWS is unconfigured: queries are planned, not executed. Application status is
  partial, counts are unknown, and no historical matches or negative claims occur.
- Public output is restricted to messages and Harness render events, not request
  task or working state as top-level channels. Hosted persistence was verified;
  dispatch render events still retain request context by contract.

## Explicit file-mode input (supported alternative)

Raw graph input (AMS invocation body wraps this once under `input`):

```json
{
  "task": {
    "intent": "dispatch",
    "payload": {
      "parts": [
        {"type": "text", "text": "Enrich the supplied triage handoff."},
        {
          "type": "resource",
          "slot": "sources",
          "resource": {"type": "file", "id": "REPLACE_WITH_CONFIRMED_TRIAGE_EXPORT_FILE_ID"}
        }
      ]
    }
  }
}
```

The placeholder is documentation only. This is for explicit file-mode clients;
the current Triage caller uses the structured form below and does not wait for an
export. File clients need access to both agent and file. Never pass a local path
or model-rewritten content.
The receiver does not invoke Triage or Recommendation itself.

<a id="structured-input-local-unpublished"></a>

## Structured input

Deployed with the full structured chain on Nov 17; safe diagnostics added Nov 18.
Triage sends its code-owned v3 object independent of managed write success. This
removes the intermediate-file dependency, not the need for working final-report
storage. Existing report schemas and confirmation requirements are unchanged.

Triage must send the **original code-owned v3 object**, not narrative, a JSON
string, a findings/LUX event object, or a model reconstruction. Exact raw graph
envelope (Python notation below uses `handoff` as the complete object):

```python
graph_input = {
    "task": {
        "intent": "dispatch",
        "payload": {
            "parts": [{
                "type": "form",
                "slot": "triage_handoff",
                "params": {"handoff": handoff},
            }]
        },
    }
}
```

The JSON path `task.payload.parts[0].params.handoff.schema` must equal
`"alert-indicators/3"`. In an AMS invocation request, wrap `graph_input` exactly
once under `input`; a remote graph client receives `graph_input` itself.
Optional `{"type":"text","text":"Enrich this handoff."}` parts are inert
prose; their content is never parsed for handoffs or IDs. No `sources` resource
may accompany the form. No second form, file, alternate slot, unknown parameter,
messages-only input, `task:null`, or text-only dispatch is accepted. Missing input
now fails schema validation rather than producing a missing-file tool outcome.
This intentional boundary tightening prevents any previous input from being reused.
The processing function also checks mode ambiguity before any read/write.

### Validation and preservation

- Params is closed (`handoff` only); the handoff itself is not projected into a
  lossy typed model. Original values, unknown extension fields, null/zero values,
  IDs, refs, source timestamps/labels, context provenance and partial statuses
  survive unchanged in `alert-enrichment/1.input`.
- Strict JSON types only: object keys must be strings; no Python tuples, sets,
  bytes or custom objects; no NaN/Infinity (including overflowed floats).
- Structured canonical serialization is at most **10,000,000 ASCII bytes**,
  nesting at most **40** (root depth zero), strings/keys at most **10,000
  characters**, and at most **1,000,000 visited values and object keys**.
  Existing v3 validation additionally enforces 1,000 incidents, 10,000 observations,
  IDs/joins, IP syntax, windows, refs, counts and field types before planning/export.
- Managed files retain the existing 10,000,000 received UTF-8 byte limit and
  strict parser (including duplicate-key rejection). Structured objects have no
  duplicate-key representation: the producer/HTTP decoder must reject duplicate
  keys before constructing the object; the receiver cannot recover overwritten keys.
- Each accepted dispatch explicitly replaces `source_file_ids` **and**
  `structured_handoff`, clearing the unused mode, and supplies a new human turn
  boundary. No message/filename/sample cache or fallback. Repeated explicit inputs
  are independent requests, not deduplicated execution.

### Receipt the Triage caller verifies

The code-owned `run_enrichment` tool result and exported JSON carry the same
`handoff_receipt`. Structured example (hash placeholder only):

```json
{
  "file_id": null,
  "sha256": "CANONICAL_PAYLOAD_SHA256",
  "schema": "alert-indicators/3",
  "input_mode": "structured",
  "payload_sha256": "CANONICAL_PAYLOAD_SHA256",
  "canonicalization": "canonical-json/1"
}
```

`canonical-json/1` = SHA-256 hex over UTF-8 bytes of Python
`json.dumps(handoff, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)` with **no trailing newline**. Arrays retain order; object keys
sort; there is no timestamp, IP, Unicode or numeric normalization. This is **not
RFC 8785**; `1` and `1.0` can hash differently. The hash covers the whole v3 object,
including unknown fields, not the Harness wrapper, mode or original alert bytes.
The local `contracts.canonical_handoff` helper validates/snapshots and returns
that hash. Triage computes it before submission and compares schema,
mode, canonicalization, null file ID, and both hash fields in the exact child's
code-owned receipt before trusting results/attachments. This does not authenticate
the source or provide distributed exactly-once processing.

File receipts retain `file_id` and `sha256` as the **exact stored-byte** digest
for existing callers. They add `input_mode="file"`, `payload_sha256` computed by
the same canonical algorithm and `canonicalization="canonical-json/1"`.
`input_sha256` remains the stored-byte hash for file mode; in structured mode it
is the canonical payload hash (there are no original file bytes).

This receiver introduces no submission client, automatic retry or downstream invocation.
Uncertain managed output writes still stop without retry and only confirmed
creations produce FileBlocks. History remains `not_configured`, counts unknown,
and application status partial where searches are unavailable. No response
actions, external intelligence, live history, inferred domains or verdicts.

Agent Kit **0.50.0** documents a form as “A structured submission under `params`”
and describes: “A form carries typed parameters.” See
[Forms](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/#forms).
Checked against pinned `v0.50.0` source
`src/spark_agent_kit/api_contracts/harness/input/{contract,channel}.py`; the local
input subclass rejects the SDK's otherwise allowed null task explicitly.

## Original receiver verification and remaining limits

The bullets below retain the original file-only checkpoint, not current release
state. Latest suite: **34/34 SDK tests passed**, zero skips, staged-core freshness
passed. Hosted structured chain verified on 0.1.5; writes stop before dispatch
with `missing_sgp_configuration`. See [verification](VERIFICATION.md).

- CLI suite: **24 tests, 22 passed, two SDK tests skipped** because the ordinary
  CLI interpreter lacks Agent Kit. This includes five managed-file receiver tests
  with injected stores, existing triage compatibility and pod-core freshness.
- The real `builder_probe` imported and constructed the graph but failed input
  validation **before model/tool execution**. It supplied plain `messages`, while
  the receiver intentionally requires the closed Harness `task` contract.
  No successful local graph-turn claim is made. Do not loosen production input
  validation merely to accommodate that probe's message-only interface.
- `builder_check`: `ready=true`, no packaging blockers, but verdict `unknown`:
  Semgrep is unavailable, so the deployment security scan did not run locally.
- API/source design checked against the bundled 0.50.0 tag, including
  `api_contracts/harness/input/contract.py`, output lifecycle extensions and
  `middleware/resources/sgp_client.py`. Bundled repository snapshot is 15 days
  old and may lag upstream; operators can refresh with `sling sources update`
  (or `sling sources update --from FILE` in a closed environment).
- Published as **Historical Enrichment POC**, agent
  `420e63bd-8220-48bd-bada-743f0daea46c`, original version **0.1.0** (historical).
  Hosted Harness v3 file receipt, actual SGP reads/writes, stored output
  channels and file events succeeded. See `AMS_RELEASE.md` for IDs/evidence.
  Donovan UI rendering and AWS access remain unverified.
- Supplemental context is supported by the local CLI but not yet an additional
  hosted attachment slot. Hosted v3 processing cannot recover omitted domains or
  registration fields.

Raw Harness input, managed output events and a no-file turn were verified after
original publication. Current entry integration propagates partial status, uses
no automatic submission retries and requires reconciliation of uncertain child
IDs; distributed exactly-once execution is not guaranteed. Only the entry needs
Donovan discovery metadata. Operator-confirmed full-chain attachments do not
prove direct downstream listing, live AWS access or image-security remediation.

## Version-matched SDK references

- [Harness task/resource input (0.50.0)](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/)
- [Managed file client (0.50.0)](https://scaleapi.github.io/spark-agent-kit/reference/platform/#spark_agent_kit.SGPResourceClient)
- [Tool outcome content (0.50.0)](https://scaleapi.github.io/spark-agent-kit/how-to/output-customization/#extend-action-payloads-and-content)
