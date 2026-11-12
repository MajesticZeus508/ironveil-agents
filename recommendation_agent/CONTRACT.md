# Recommendation input/output contract — alert-recommendations/1

This describes the implemented POC, not a new producer schema or a comprehensive
formal JSON Schema. `ams/core.py` is the executable validation contract.
Current staging 0.1.4 retains the original schemas/prompt with concurrency bounded to two
and additive elapsed/stage diagnostics; source was released in 0.1.2.

## Input

One UTF-8 JSON managed file: `alert-enrichment/1`, containing the original
`alert-indicators/3` object under `input`. Accept the Enrichment JSON export,
not raw findings, a Triage export alone, or a Markdown report. Hosted dispatch
and a copy/paste AMS request are in [README.md](README.md#test-in-ams-invoke).
Only current-request `sources` file references are used. User prose cannot select
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

- `schema`, UTC `generated_at`, and `source_sha256` of the received file bytes.
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
- Inline report is omitted above 18,000 characters (`report=null`); files remain
  available. Only confirmed managed creations produce attachment blocks.

## Compatibility and scope

No schema v4 inference, domain invention, live reputation lookup, AWS search,
automatic downstream invocation, threat verdict or alert closure is implemented.
The separate Triage entry does automatically invoke this receiver; the sentence
above refers to capabilities of this agent, not absence of workflow integration.
Model-based prioritization, portfolio executive synthesis, organization-specific
playbooks, classification propagation and complete semantic validation are deferred.
Schema/behavior changes need explicit design, regression tests and a new approved
release; do not silently relabel upstream data or discard its partial status.
