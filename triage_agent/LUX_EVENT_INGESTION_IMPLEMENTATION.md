# LUX event adapter — local implementation, 2026-11-12

> Historical implementation record. The adapter and reviewed compatibility are
> deployed in the current 0.1.30 entry; latest raw-Harness hosted chain passed
> both handoffs and 1/1 analysis. Storage is blocked separately by missing staging
> SGP runtime configuration. See [current envelope/workflow](WORKFLOW.md) and
> [Nov 18 evidence](DIAGNOSTIC_RELEASE_2026_11_18.md). The local-only/deploy-first
> instructions below retain the earlier checkpoint; they do not establish live
> Events-rule configuration or authorize changing a rule during housekeeping.

**2026-11-13 follow-up:** structured staging 0.1.25 delivery was inspected; the
latest producer payload exposes unknown entity/measure fields. See
[local compatibility rules, captured evidence, tests and downstream release gate](LUX_PAYLOAD_COMPATIBILITY_2026_11_13.md).
The historical implementation/publication status below describes the earlier pass.

Status: implemented in editable **Dev-targeted** `plugins/alert_triage/` only.
Not published; no live rule, staging snapshot, or downstream agent changed.

## Evidence and selected contract

The operator confirmed `LUX_Alert.md` is a payload copied from Events Log:
one synthetic `swoop-ueba-finding/1` object directly, with no outer event envelope.
The supplied rule template currently interpolates it into prose:
`Process this event: {{event}}`. That legacy text is intentionally NOT parsed.

The new input uses Agent Kit 0.50.0 `FormPart`, slot `lux_event`, with a closed
`params` object containing `event`. The finding's fields remain unmodified and
are validated by the existing parser. No arbitrary envelope paths are searched.
Only the observed hourly detector/measure pair was added:
`egress_volume_hourly` / `distinct destinations of uploads of 100 MB or more, per hour`.

SDK reference: [Harness forms](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/#forms).
Checked against the bundled `spark-agent-kit` source tag `v0.50.0`,
`src/spark_agent_kit/api_contracts/harness/input/contract.py`.

## Rule mapping for a future approved deployment

Do NOT apply this to the currently published staging agent: it does not yet
accept the new form. First deploy an approved candidate to the intended target.
The editable source points to Dev downstream receivers; a staging candidate must
be configured separately without editing `releases/staging_0_1_24/`.

Replace the agent input with the following only after that deployment:

```json
{
  "task": {
    "intent": "dispatch",
    "payload": {
      "parts": [
        {
          "type": "form",
          "slot": "lux_event",
          "params": {
            "event": "{{event}}"
          }
        }
      ]
    }
  }
}
```

The UI help in the supplied screenshot documents exact `{{event}}` replacement
as the whole event payload, versus interpolation inside prose as text. Hosted
verification must confirm `params.event` arrives as an object, not a JSON string.
Leave **Include trigger context** unchecked: no `event_trigger` field is declared.

## Bounds, isolation, and provenance

- One event = one finding; batches/wrappers/arrays are not accepted on this path.
- Maximum canonical finding serialization: 1,000,000 UTF-8 bytes. The entire event
  dispatch task serialization is independently bounded to the same limit.
- File uploads retain their existing limits and parser; file/event inputs together
  and multiple events fail validation rather than silently choosing one.
- Every fresh dispatch resets both input channels. Text-only dispatch never reuses
  an earlier event/file, and null tasks are rejected. Checkpoint resume is unchanged.
- Existing deterministic extraction, deferred narrative, five stages, verified
  export receipts, partial status, and no automatic submission/write retries remain.
- `run.event_receipt` records handling time, accepted finding IDs, payload SHA-256,
  input mode, and explicit hash basis. The hash covers `json.dumps` with sorted keys,
  compact separators, `ensure_ascii=False`, `allow_nan=False`, encoded UTF-8—not
  original LUX transport bytes. Handling time is not producer/event emission time.
- Spark event/source IDs are unknown (`null`), since the supplied payload lacks
  delivery metadata. Finding IDs are never relabeled as Spark IDs.
- Later stage statuses retain that parent receipt, including downstream failures.
  The strict `alert-indicators/3` file schema is unchanged; its existing source hash
  and finding references link it to the parent receipt. Delivery metadata is not
  added to downstream report files. Cross-delivery deduplication is NOT implemented.
- Synthetic data only; no AWS/history enablement, LUX write-back, or response actions.

## Verification

`python3 -m unittest discover -s tests -v` from `triage_agent/`:
**66 tests: 49 passed, 17 skipped, zero failures**. The six new tests cover exact
hourly pair/preservation, equivalent file/event extraction, hash receipt, malformed
and oversized payloads, ambiguity, invalid findings, untrusted strings, uncertain
writes without retries, and typed input/fresh-dispatch isolation. The typed contract
test is among the SDK-dependent skips; the other five new tests passed.

Sample result: **one accepted finding, one group, 10 observations**, preserving the
reported 12 destinations separately from the 10-row evidence sample.

`builder_probe` imported/constructed the graph (including import-time contract
assertions) but failed before execution because the tool sends native `messages`
input instead of this agent's required Harness `task`. Fault: `harness`; zero model
calls. No claim of successful local full-graph event execution or hosted acceptance.
Do not widen the public schema merely to accommodate the probe.

`builder_check`: **ready=true**, zero blockers. Semgrep unavailable: security scan
did not run and remains unknown, not clean.

Remaining gates: approved target/configuration, deployment/security
checks, actual Spark rule substitution/identity/permissions, and end-to-end synthetic
event acceptance. Repeated-delivery ownership and durable event correlation remain
operational decisions before enabling unattended traffic.

## Follow-up managed testing

Local-only `builder_probe(name="triage_agent/tests/reliability_verify")` completed
successfully, returning **SDK tests and five-stage checkpoint workflow passed**.
Managed runtime results: **67 Triage tests passed, 15 Recommendation tests passed,
zero skips**. The Triage suite ran in 118.300s; Recommendation in 0.065s.

`test_event_workflow.py` passes the actual structured form into the application
graph with an in-memory checkpointer and tests:

- all five stages and five projected file attachments;
- real deterministic extraction of the supplied finding (one finding, ten rows);
- the same event receipt in every later stage status;
- text-only input on the same checkpointed thread does not reuse the event;
- a distinct subsequent finding receives a new payload hash and finding ID;
- uncertain Enrichment collection preserves the new receipt/export, stops routing,
  and does not submit Recommendation or automatically retry.

Resource clients and downstream submission/collection are stubbed for this new
workflow test. An initial test setup failure exposed a captured resource-client
reference: the test now reloads the application graph under the public client
stub before tool construction. No SDK internals were modified.

The probe recorded **12 model-gateway calls, zero refusals** during the complete
verification run; this is therefore not an inference-free/offline verification.
Those calls were not individually attributed. No hosted event-path acceptance,
live rule update, publication, or real file/downstream behavior is established
by these mocked workflow tests.

The runtime also warned about checkpoint deserialization of the application task
type being unregistered for a future stricter serializer. It did not block these
0.50.0 tests; compatibility with future SDK versions is not established.
