# LUX → Spark Events → AMS Triage integration plan

Date: 2026-11-12
Status: Proposed; awaiting a representative LUX event and rule invocation mapping.

## Objective

Automatically receive LUX alerts through Spark Events and run the existing
IronVeil investigation workflow in AMS:

```text
Local LUX instance
    → Spark Events: "Swoop Pattern of Life" source
    → Event-matching rule and invocation mapping
    → AMS Triage entry
    → Historical Enrichment
    → Recommendations
    → Analyst outputs
```

The operator and engineer have identified an existing Spark event source and the
rule-based connection mechanism. The source's configuration, event schema, and
AMS invocation mapping have not yet been inspected for this implementation.

Success means more than a rule firing: the intended finding records must reach
Triage intact, be validated and extracted, and produce outputs traceable to the
originating event.

## Current implementation and integration gap

- Triage receives a strict Harness dispatch input with text and a managed file
  reference in the `sources` slot.
- It reads exactly one current-invocation findings file, limited to 1,000,000
  bytes and 100 records.
- The parser accepts JSONL, a JSON array, a single finding, or
  `{"findings": [...]}`. Findings use `swoop-ueba-finding/1` and supported
  detector/measure pairs.
- Default hosted Triage performs deterministic extraction without Triage model
  calls, then orchestrates Enrichment and Recommendation.
- Arbitrary event JSON or alert JSON supplied as chat text is not currently an
  ingestion path.
- Finding deduplication and incident grouping operate within each invocation;
  they do not provide cross-delivery deduplication or cross-run correlation.

The first design decision is whether the Spark rule can supply the existing
managed-file contract or whether Triage needs a typed inline-event input.

## 1. Confirm the event and rule contracts

- [ ] Obtain a representative synthetic or redacted event emitted by LUX,
      including its Spark event envelope and original finding payload.
- [ ] Inspect the existing **Swoop Pattern of Life** source with the engineer;
      confirm the local LUX instance publishes to the intended environment,
      source, and tenant.
- [ ] Capture the rule's exact AMS invocation body, including the input mapping
      and any thread/configuration fields outside the agent input.
- [ ] Identify the event ID, LUX alert ID, producer/source identity, event time,
      and location of the original finding records.
- [ ] Confirm whether one event contains one finding, multiple findings, or a
      reference to a payload; identify any evidence truncation in transport.
- [ ] Confirm delivery/replay behavior, ordering, retry policy, concurrency,
      payload limits, and any platform-supported idempotency mechanism.
- [ ] Check the deployed SDK's supported typed event/dispatch inputs before
      selecting a contract extension.

**Deliverable:** a captured example event and exact expected AMS input, plus a
field-mapping table. Do not infer payload paths or rule syntax from the older
LUX SGP application/variant documentation: it describes a different interface.

## 2. Select and document the ingestion contract

- [ ] Select the smallest supported integration based on the captured request:
      - **Managed-file mapping:** use the existing `sources` contract if the
        integration can create an accessible managed file and reference it.
      - **Typed inline-event mapping:** add an explicitly declared input when
        the rule delivers the finding payload inline.
- [ ] Define how the LUX/Spark envelope is separated from original findings.
      Use explicit schema fields and paths rather than searching arbitrary text.
- [ ] Preserve all supplied finding IDs, incident keys, timestamps, detector
      metrics, evidence, source labels, and synthetic flags.
- [ ] Specify behavior when both file and event inputs are present; reject
      ambiguous requests rather than silently choosing one.
- [ ] Define missing-payload, malformed-envelope, unsupported-schema, oversized,
      and zero-valid-finding outcomes.
- [ ] Define a bounded input policy for inline events; retain the existing file
      limits unless a separately justified change is approved. Account for both
      event-envelope size and finding-payload size.
- [ ] Define the provenance receipt: event/LUX identifiers, received timestamp,
      input mode, and payload hash. Specify whether the hash covers original
      received bytes or a documented serialization of an already-decoded object.
- [ ] Decide where delivery correlation metadata belongs in the output. Review
      downstream validators before adding fields or changing schema versions.

**Deliverable:** an approved input and provenance contract, with no dependence on
free-text instructions to select the payload or route the investigation.

## 3. Implement the Triage input adapter, if required

- [ ] Add the selected input path using version-matched SDK APIs.
- [ ] Normalize the input into the existing validation/extraction pipeline;
      reuse the parser and analysis logic rather than creating a second engine.
- [ ] Preserve current managed-file behavior for Donovan uploads.
- [ ] Carry event correlation through workflow status and outputs according to
      the agreed contract, without overloading managed-file ID fields.
- [ ] Ensure every invocation uses its own explicit input, with no stale-event,
      previous-upload, local-path, or bundled-fixture fallback.
- [ ] Keep alert content as untrusted data and preserve explicit extraction
      errors, partial status, and downstream failure reporting.

If the rule supplies the existing managed-file contract, this step may consist
of verification and only the agreed correlation additions.

### Expected implementation locations

| File | Potential change |
|---|---|
| `plugins/alert_triage/contracts.py` | Typed input and invocation-state preparation |
| `plugins/alert_triage/hosted.py` | File/event input normalization and receipts |
| `plugins/alert_triage/stages.py` | Input consumption and stage correlation |
| `plugins/alert_triage/export.py` | Provenance additions, if contract-approved |
| `plugins/alert_triage/file_first.py` | Routing/error wording if necessary |
| `tests/` | Contract, ingestion, isolation, and workflow regression coverage |

These are candidate edit points, not a requirement to modify every file.
Editable source currently targets Dev. The retained staging release
`releases/staging_0_1_24/` must remain a preserved snapshot; any staging candidate
must use the appropriate staging configuration rather than publishing Dev
receiver targets accidentally.

## 4. Configure the Spark rule and delivery behavior

- [ ] Create a narrowly scoped test rule using the existing source and the
      actual supported rule configuration.
- [ ] Target the intended AMS Triage entry and configure the agreed input mapping.
- [ ] Confirm the invoking identity can invoke Triage and, for file inputs,
      read the referenced file. Verify the downstream handoffs under that identity.
- [ ] Start with a fresh investigation thread per test event/batch. Verify any
      source-provided thread reuse before enabling it.
- [ ] Decide delivery-deduplication ownership using confirmed platform features.
      Record event identity, payload hash, and invocation identity durably where
      the integration supports it; define how changed content under the same ID
      is handled.
- [ ] Define reconciliation after an uncertain submission. Do not blindly retry
      an invocation that may already be running.
- [ ] Set an initial concurrency/rate bound appropriate to the full workflow.
      The entry launches Recommendation automatically, and prior end-to-end
      runs took several minutes.
- [ ] Choose one event per run or a bounded batch policy. Keep related findings
      together when grouped incident analysis is required; specify behavior for
      late or out-of-order findings.

**Deliverable:** one documented rule configuration with explicit input mapping,
delivery behavior, and correlation ownership.

## 5. Verify locally and through the hosted event path

### Offline checks

- [ ] Turn the representative event into a sanitized fixture under `tests/`.
- [ ] Verify the exact rule-mapped input against the declared agent schema.
- [ ] Compare file and event ingestion of equivalent findings: accepted IDs,
      incident grouping, observations, and metrics must match; transport-specific
      provenance may differ.
- [ ] Cover missing/invalid payloads, wrong schemas, bounds, ambiguous inputs,
      mixed valid/invalid findings, and input isolation between invocations.
- [ ] Verify correlation survives successful stages and downstream failures.
- [ ] Test duplicate-delivery and uncertain-submission behavior at the component
      that owns it.
- [ ] Run `python3 -m unittest discover -s tests -v` from `triage_agent/`.
      Run SDK-dependent checks in the compatible environment; record any skips.

### Hosted acceptance

- [ ] Publish an approved test candidate to the agreed test target and enable
      the narrowly scoped rule.
- [ ] Emit one known synthetic event from local LUX through the actual source.
- [ ] Record source/event identity, rule match, AMS parent invocation, child
      invocations, payload receipt, and confirmed output file IDs.
- [ ] Confirm all expected findings and evidence were received without transport
      loss or unintended transformation.
- [ ] Confirm Triage extraction and the expected downstream stages run, with
      confirmed attachments and application-level status available.
- [ ] Exercise malformed input, repeat delivery, two distinct events, and
      timeout/reconciliation behavior in controlled tests.
- [ ] Verify the agreed duplicate-handling behavior and that distinct events
      cannot receive each other's input or output.

**Acceptance criteria:**

1. A LUX event triggers the intended AMS entry without manual attachment.
2. Finding IDs, counts, evidence, and payload receipt match the submitted input.
3. Equivalent file/event inputs produce equivalent deterministic extraction.
4. Outputs and failures are traceable to the originating LUX/Spark event.
5. Invalid input has explicit errors; no stale input or fabricated success occurs.
6. Repeat delivery follows the documented policy, and uncertain submissions are
   reconciled before retry.
7. Existing Donovan upload regressions pass.

Successful delivery is evaluated separately from model quality and historical
availability. Existing AWS `not_configured`, deferred Triage narrative, and any
Recommendation failures must remain visible; platform completion alone does not
establish complete investigation results.

## 6. Release and operational handoff

- [ ] Record the tested rule mapping, event schema, agent version, SDK version,
      target environment, and evidence from hosted acceptance.
- [ ] Obtain operator approval for the target release and rule activation.
- [ ] Document how to pause the rule, reconcile in-flight invocations, and
      restore the previous rule mapping/agent version.
- [ ] Update the Triage README and operator runbook with event-ingestion usage,
      limits, status interpretation, and troubleshooting.
- [ ] For non-synthetic alerts, resolve the existing source-marking propagation
      gap and confirm handling requirements before rollout.

## Decisions pending the sample event

| Question | Why it matters |
|---|---|
| What exact input does the Spark rule send to AMS? | Determines configuration-only integration versus a typed input adapter. |
| Where are the original findings and full evidence? | Determines explicit payload extraction and compatibility. |
| Is one event a finding or a complete incident batch? | Determines grouping behavior and batching needs. |
| What IDs and delivery guarantees are supplied? | Determines correlation, replay, and deduplication ownership. |
| Does the rule reuse threads? | Determines isolation and concurrency requirements. |
| Where should analysts retrieve results? | Determines whether AMS files/status suffice or a LUX write-back is a separate requirement. |

## Scope boundary

This feature adds event-triggered ingestion to the existing investigation entry.
ATT&CK mapping is a separate Recommendation experiment. LUX report write-back,
live history integration, and persistent cross-event incident aggregation require
their own explicit requirements if needed.

## Immediate next step

Obtain **one representative LUX event and the Spark rule's resulting AMS request**.
Use those two artifacts to finalize the input contract before implementation.
