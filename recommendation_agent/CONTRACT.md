# Recommendation input/output contract — alert-recommendations/1

This describes the implemented POC, not a new producer schema or a comprehensive
formal JSON Schema. `ams/core.py` is the executable validation contract.
Current staging checkpoint: **0.1.9**, 2026-11-18. Structured input and safe-write
diagnostics are deployed. Output schemas remain unchanged; reviewed LUX prompt
compatibility, concurrency two and bounded incident diagnostics are retained.

## Input

Exactly one explicit structured form or UTF-8 JSON managed file:
`alert-enrichment/1`, containing the original
`alert-indicators/3` object under `input`. Accept the Enrichment JSON export,
not raw findings, a Triage export alone, or a Markdown report. Hosted dispatch
and a copy/paste AMS request are in [README.md](README.md#test-in-ams-invoke).
Only current-request `sources` references or `enrichment_handoff` form are used. User prose cannot select
a local path, alternate source, model, lookup service or response tool.

| Bound | Current value |
|---|---:|
| Input bytes | 20,000,000 |
| Incidents | 100 |
| Observations | 10,000 |
| Historical query results | 100,000 |
| Recursive nesting | 40 |
| Input string characters | 10,000 |
| Per-incident serialized packet bytes | 180,000 |
| Per-export UTF-8 bytes | 24,000,000 |

Duplicate JSON keys, nonfinite values, invalid IDs/joins/counts, malformed IPs,
invalid windows and contradictory search outcomes are rejected. Bounds refuse
the input; they do not silently truncate it. Validation is intentionally bounded,
not proof of source authenticity or complete semantic consistency.

The packet includes incident context, every linked supplied observation and
historical query result, optional explicitly linked supplemental context, source,
policy, capabilities, extraction status and limitations. There is no enrichment
lookup or autonomous action. Upstream suggestions remain untrusted model context.

<a id="structured-receiver-local-unpublished"></a>

## Structured receiver

Enrichment structured output and Triage forwarding are deployed and hosted-verified;
the initial ARP publish blocker was resolved on an authorized retry. SDK suite
26/26 passes. Raw graph input, using Python notation where
`enrichment` is the complete code-owned object:

```python
{
    "task": {
        "intent": "dispatch",
        "payload": {
            "parts": [{
                "type": "form",
                "slot": "enrichment_handoff",
                "params": {"enrichment": enrichment},
            }]
        },
    }
}
```

`params.enrichment.schema` must be `alert-enrichment/1`; `input.schema` inside it
must be `alert-indicators/3`. This is **not** just an indicator list, JSON string,
Markdown report or original LUX alert. AMS HTTP bodies wrap the graph input once
under `input`; graph clients receive the graph input itself. Optional text parts
are prose only, never parsed for data/IDs. Params permits only `enrichment`.

Exactly one file in `sources` **or** one `enrichment_handoff` form is required.
Mixed/repeated modes, missing input, `task:null`, messages-only and text-only
requests fail validation before analysis. (The old file-only version's
text-only `missing_enrichment` response is historical behavior.) Each accepted
dispatch replaces both `source_file_ids` and `structured_enrichment`, clearing
the unused mode and creating a fresh turn boundary. No prior input recovery,
sample/filename fallback, automatic mode downgrade or retry.

Structured JSON uses exact built-in JSON types, string keys and finite numbers;
no coercion of tuples, bytes, custom objects or numeric keys. Bounds: 20,000,000
canonical serialized ASCII bytes, depth 40, 10,000 characters per key/string and
2,000,000 visited values/keys. The existing semantic validator and packet builder
enforce all incident/observation/query/coverage/reference and per-incident model
packet limits before inference/export. Unknown fields remain in the snapshot and
hash; original catalog values/provenance/unknowns are not rewritten. Output keeps
the existing selective evidence/upstream projection, not a new full-input echo.

Managed files retain their existing received UTF-8 byte limit and strict parser,
including duplicate-key rejection. A decoded object cannot represent duplicate
keys: the producer/HTTP decoder must reject those before constructing the object.

The code-owned `run_recommendation` tool result adds `handoff_receipt`:

```json
{
  "schema": "alert-enrichment/1",
  "input_mode": "structured",
  "file_id": null,
  "sha256": "CANONICAL_PAYLOAD_SHA256",
  "payload_sha256": "CANONICAL_PAYLOAD_SHA256",
  "canonicalization": "canonical-json/1"
}
```

`canonical-json/1` = SHA-256 hex over ASCII (equivalently UTF-8) bytes of
`json.dumps(enrichment, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)`, with no trailing newline. Not RFC 8785: there is no timestamp,
Unicode/IP or numeric normalization. Arrays retain order, and `1`/`1.0` can hash
differently. All fields of the full enrichment object, including `generated_at`,
unknown extensions and any upstream receipt, participate; the Harness wrapper
does not. `ams.structured_input.canonical_payload` validates/snapshots and returns
the digest.

File receipts use `input_mode="file"`, exact managed `file_id`, `sha256` of the
stored bytes and `payload_sha256` from the same canonical algorithm. Existing
`received_file_id` and `source_sha256` retain file semantics; structured mode
returns null and canonical hash respectively. `alert-recommendations/1` exports
remain unchanged; their existing `source_sha256` is canonical in structured mode.
The transport receipt lives in tool status, not a new report schema field.

Triage verifies all six receipt fields against its pre-submission hash before
trusting outputs; action-scoped FileBlocks still attest only confirmed writes.
Both intermediate-file dependencies are removed. Hosted SDK/checkpoint processing
and 1/1 live narrative succeeded on the latest releases, but files are blocked by
missing staging runtime SGP configuration before dispatch. No lookups/actions or
model retries added. See [workflow](../triage_agent/WORKFLOW.md) and
[diagnostic release](../triage_agent/DIAGNOSTIC_RELEASE_2026_11_18.md).

Agent Kit 0.50.0 describes: “A form carries typed parameters.”
[Forms](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/#forms).
Implementation follows the pinned Harness `FormPart`/task preparation pattern
already checked at `v0.50.0:src/spark_agent_kit/api_contracts/harness/input/{contract,channel}.py`.

## Evidence references

Each output incident has a code-owned `evidence_catalog`:

| Key | Meaning |
|---|---|
| `incident` | Original incident/context; narrative is not independent network evidence |
| `O1`, `O2`, … | Supplied observations, including original observation IDs and finding refs |
| `H1`, `H2`, … | Historical query results, including query IDs, criteria, coverage and samples |
| `C1`, `C2`, … | Optional operator-supplied supplemental context; unverified |

Each entry retains `source_path` (JSON pointer into the received Enrichment file),
`kind`, and original `value`. Keys are local to each incident/output, not global
indicator identities. `O*`/`H*` numbering reflects input order; `C*` numbering
reflects its original supplemental-array position. Use original IDs for joins.
Observation refs retain finding ID, source line/record index and evidence index;
interpret source position using `upstream.triage_source.source_location_kind`.

## Output: alert-recommendations/1

`recommendation_results.json` contains:

- `schema`, UTC `generated_at`, and `source_sha256`: exact received file bytes in
  file mode, canonical full input payload in structured mode.
- `upstream`: Enrichment run/source, extraction, triage source/context provenance,
  policy, capabilities and Enrichment limitations, retained separately from advice.
- `provenance`: configured model, generation method, knowledge basis and fixed
  prompt hash. Training knowledge is not current intelligence or incident evidence.
- `run`: status and incident/completed/failed counts.
- Per incident: `analysis_duration_seconds` and `diagnostic_stage`. Elapsed time
  includes semaphore waiting; the 95s model-call timeout starts after admission.
  These values are not isolated provider-inference durations.
- `human_review_required: true`, `actions_executed: []` and fixed limitations.
- `incidents`: code-owned entity/window/ID, original priority, synthetic flag,
  `needs_review`, upstream context availability, catalog and analysis status/error.

On success, each incident's `narrative` has:

| Field | Model-output bound |
|---|---|
| `summary`, `assessment` | Each ≤700 characters |
| `evidence` | 1–3 claims ≤300 characters; each has 1–6 catalog refs |
| `recommendations` | 2–3 ordered objects: action ≤300, rationale ≤250, decision_if ≤300 characters |
| Recommendation controls | category investigate/monitor/escalate/containment, requires_approval boolean, catalog refs |
| `escalation_trigger` | ≤400 characters |
| `limitations` | 1–3 strings, each ≤250 characters |
| `target_observation_ids` | 0–3 existing observation IDs from this incident |

Provider JSON-schema constraints supplement local validation. Local checks cover
structure, references, explicit targets, lexical IP/domain mentions and a limited
disruptive-action vocabulary. Those checks do **not** establish factual entailment,
detect every unsafe recommendation, or remove the need for analyst judgment.
Containment proposals require approval; no execution capability exists.

`recommendation_report.md` renders the validated data, including a fixed closure /
de-escalation review gate. It is not a second model-generated report. JSON remains
the traceable source for full evidence; the readable report only highlights claims.

## Status and failure semantics

- AMS platform `completed` means the invocation finished, not that every model
  analysis or enrichment succeeded.
- Application `partial` if any incident narrative fails, upstream Enrichment or
  extraction is not completed, extraction errors exist, or context is unavailable.
- `completed` requires incident outputs with none of those conditions. Empty
  input can remain partial because upstream empty is not completed in this POC;
  callers should inspect counts as well as status rather than assume `empty`.
- Narrative failure: `narrative=null`, `analysis_status=failed`; evidence remains.
  Error codes are sanitized (`validation_rejected`, `timeout`, `model_request_failed`).
  Local narrative-validation failures can include a fixed `validation_code`.
- `not_configured`, `unknown`, `unsupported`, `insufficient_input` and historical
  `error` are not clean negatives. `seen` does not imply benignity. A covered
  negative applies only to that criterion/window, not “never seen.”
- Hosted `export_status` is separate: two confirmed writes mean `completed`, even
  when analysis is partial. Uncertain writes stop further exports and are not retried.
- Safe `exports[].write_diagnostic` and `export_diagnostics` are tool status, not
  report schema fields. Current staging: `missing_sgp_configuration`, ValueError,
  HTTP null, request_may_have_been_sent=false; no upload dispatched or file confirmed.
- Inline report is omitted above 18,000 characters (`report=null`); a file is
  available only if its managed write succeeded. Only confirmed creations produce blocks.

## Compatibility and scope

### Deployed LUX compatibility (reviewed 2026-11-13 and 2026-11-16)

Accept the exact entity `{type: "unknown", id: null, site: null}` only for
incidents with `synthetic: true` and source `["swoop/valhalla/simulated"]`.
All three keys are required; other unknown shapes and null IDs on known types
remain invalid. Original entity, quality issues, metrics supplied inside those
issues, and all observations are preserved in the evidence catalog. No source
IP/site, related value or placeholder incident key establishes entity identity.

The fixed prompt forbids aliasing `to AMS egress_volume` / `unknown` to canonical
egress semantics or deriving units/thresholds from samples. The readable report
adds code-owned identity/measure warnings, even on narrative failure. Unknown
entity or `unknown_measure_semantics` keeps application status `partial` despite
successful narrative. Schemas, input limits, response controls and retries are
unchanged. These checks are not a semantic guarantee about model prose.

No schema v4 inference, domain invention, live reputation lookup, AWS search,
automatic downstream invocation, threat verdict or alert closure is implemented.
The separate Triage entry does automatically invoke this receiver; the sentence
above refers to capabilities of this agent, not absence of workflow integration.
Model-based prioritization, portfolio executive synthesis, organization-specific
playbooks, classification propagation and complete semantic validation are deferred.
Schema/behavior changes need explicit design, regression tests and a new approved
release; do not silently relabel upstream data or discard its partial status.
