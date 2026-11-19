# MITRE ATT&CK integration — plan and test checklist

Date: 2026-11-12
Status: Proposed future work; implementation and deployment have not started.

## Goal

Give analysts evidence-backed ATT&CK technique and sub-technique mappings in
incident summaries, with clear rationale, uncertainty, and follow-up checks.
An incident may legitimately return **insufficient evidence to map**.

This document is saved with Enrichment for future development. It captures the
earlier Recommendation-agent POC proposal and an optional Enrichment role in
supplying the ATT&CK reference material.

## Proposed ownership

| Agent | Responsibility |
|---|---|
| Triage | Preserve original observations and any explicitly supplied technique labels and provenance, if exposed by an approved input/output contract. |
| Enrichment | Supply historical context; optionally retrieve relevant definitions from a bundled, version-pinned ATT&CK catalog. Retrieved techniques are candidates, not established incident findings. |
| Recommendation | Assess whether observations support candidate techniques; explain mappings and uncertainties in the analyst deliverable. |

**Recommended initial experiment:** a separate Recommendation ATT&CK POC
deployment with its own bundled catalog and retrieval, invoked directly with the
same Enrichment exports as the baseline agent. This isolates the mapping change
and permits comparison before changing the integrated chain.

**Possible later integration:** move catalog retrieval into Enrichment and pass
candidate definitions downstream. Confirm this ownership explicitly before
implementation. Performing final model-based mapping inside Enrichment instead
would expand its current deterministic historical-search role and needs a
separate design decision.

## Current constraints to carry forward

- Enrichment consumes `alert-indicators/3` and emits `alert-enrichment/1`.
- Recommendation consumes that export and emits `alert-recommendations/1`.
- The v3 handoff omits full detector metrics/baselines, the full domain inventory,
  and endpoint/application details. Do not reconstruct omitted facts from labels.
- Historical availability, upstream partial status, original IDs, evidence
  references, and synthetic flags must remain visible.
- ATT&CK definitions are reference knowledge, not incident evidence or live
  threat intelligence. A catalog match does not establish compromise.

## 1. Select and prepare the ATT&CK dataset

### Operator checklist

- [ ] Select **Enterprise ATT&CK** as the initial domain; confirm whether ICS or
      Mobile is needed later.
- [ ] Obtain a versioned STIX 2.1 JSON collection from the official repository:
      <https://github.com/mitre-attack/attack-stix-data/tree/master/enterprise-attack>.
- [ ] Record the chosen release, exact source URL/repository revision, download
      date, SHA-256 checksum, and applicable attribution/license information.

### Implementation checklist

- [ ] Preserve the original snapshot and generate a reproducible searchable
      reference containing technique IDs, names, full descriptions, tactics,
      platforms, official URLs, and parent/sub-technique relationships.
- [ ] Retain revoked/deprecated status; exclude inactive entries from new mapping
      candidates while allowing explicitly labeled validation of historical IDs.
- [ ] Validate catalog IDs, relationship targets, and the selected ATT&CK domain.
- [ ] Package the reference as an explicit deployment asset. Verify packaging
      rules; keep received handoffs, alert fixtures, and outputs out of production
      fixture directories.
- [ ] Load/search the reference in application code and pass relevant definitions
      into the model request. Merely bundling a file does not expose it to the model.

Use a local snapshot initially. Runtime TAXII/API access is optional future work
and would require its own access, update, and failure-handling design.

## 2. Define retrieval and mapping behavior

```text
Incident observations + available history
    → Search pinned ATT&CK catalog
    → Candidate definitions + incident evidence
    → Recommendation assessment
    → Catalog/reference validation
    → Structured mappings + rendered analyst report
```

- [ ] Start with local text search; document searchable fields, query construction,
      candidate limits, and model-context budget.
- [ ] Evaluate whether retrieval finds analyst-expected techniques before adding
      embeddings or a vector database.
- [ ] Preserve candidate IDs, catalog version, and retrieval method. A retrieval
      score is relevance, not mapping confidence or attack probability.
- [ ] Require reasoning from actual behavior. Fanout alone does not establish
      scanning; high outbound bytes do not establish exfiltration; an unusual
      destination does not establish command-and-control.
- [ ] Require stronger, specific evidence for sub-techniques; allow parent-level
      mappings when only the broader behavior is supported.
- [ ] Separate source-supplied technique labels, retrieved candidates, and
      model-proposed mappings. None is independent corroboration of another.
- [ ] Permit no mapping and record why. Distinguish insufficient evidence from
      retrieval failure, invalid catalog data, and model failure.
- [ ] Treat alert text and upstream suggestions as data, not instructions.

## 3. Define the output and handoff contract

Proposed per-incident assessment fields, to finalize before coding:

| Field | Purpose |
|---|---|
| Assessment status | Mapped, insufficient evidence, or explicit processing failure |
| Technique ID/name | Validated against the pinned catalog |
| Tactics | Catalog-associated tactics; identify incident-specific interpretation separately |
| Evidence references | Original observation IDs and source paths supporting the proposed mapping |
| Rationale | Explanation of how supplied behavior fits the definition |
| Assessment strength | Qualitative, rubric-defined judgment; not a calibrated probability |
| Uncertainties/missing evidence | What limits the mapping and what to check next |
| Catalog provenance | ATT&CK release, snapshot hash, and technique URL |
| Generation provenance | Model/prompt and retrieval configuration identifiers |

- [ ] Code supplies names, URLs, and catalog metadata from validated IDs.
- [ ] Validate incident-local evidence joins and parent/sub-technique relationships.
- [ ] Render Markdown from the same validated structured output.
- [ ] Keep reference definitions separate from observed evidence in catalogs and
      reports. A valid evidence reference does not prove semantic support.
- [ ] Specify compatibility and explicit schema versioning for output changes.
      Review strict downstream validators before extending either handoff.
- [ ] If retrieval moves to Enrichment, define a candidate-reference section and
      Recommendation consumption rules; do not silently change `alert-enrichment/1`.
- [ ] Preserve upstream partial status and unavailable-history outcomes even when
      ATT&CK mapping succeeds.

## 4. Build an isolated POC

- [ ] Record the existing Recommendation source/version, model configuration,
      prompt, and baseline outputs.
- [ ] Create a separate experimental deployment, such as
      **Recommendation ATT&CK POC**, after approval of the test target.
- [ ] Keep the experiment's code, catalog assets, tests, and outputs under the
      owning agent directory with a clear baseline relationship.
- [ ] Add retrieval, bounded mapping output, validation, and report rendering.
- [ ] Invoke the experiment directly with existing `enrichment_results.json`
      inputs before changing Triage's automatic downstream routing.
- [ ] Compare baseline and experiment using identical inputs and unchanged model
      settings where possible. Record added calls, tokens, latency, and failures.

If Enrichment is later selected as retrieval owner:

- [ ] Read `AGENTS.md`, `README.md`, `S3_INTEGRATION.md`, `HISTORICAL_SEARCH.md`,
      and `AMS_RELEASE.md` before implementation.
- [ ] Keep core changes in root-owned files and stage them through
      `python3 prepare_pod.py`; edit hosted-specific files in `ams/` directly.
- [ ] Run `python3 -m unittest discover -s tests -v`, followed by
      `python3 prepare_pod.py --check` from `enrichment_agent/`.
- [ ] Add a catalog asset-copy/freshness check if needed; verify the actual hosted
      bundle contains the selected catalog and no alert fixtures.

Recommendation changes must follow its own scoped instructions and tests. This
plan does not authorize publication or changes to other agents.

## 5. Prepare and run the evaluation

### Operator preparation

- [ ] Assemble **10–15 synthetic or redacted incidents** using existing Enrichment
      exports where possible.
- [ ] Include clear behavioral matches, ambiguous cases, benign alternatives,
      and insufficient-evidence cases.
- [ ] Have an analyst record expected techniques, acceptable alternatives, and
      supporting observations before seeing model results.
- [ ] Include parent-versus-sub-technique cases and examples that expose sparse
      network-only telemetry. Any added telemetry needs an explicit input contract.
- [ ] Agree on acceptance thresholds before running the experiment.

### Implementation and analyst review

- [ ] Test catalog validation, inactive IDs, evidence joins, missing reference
      assets, bounded retrieval, and explicit processing failures offline.
- [ ] Run the owning agent's existing regression checks.
- [ ] Measure retrieval recall separately from final mapping quality.
- [ ] Review unsupported mappings, missed supported techniques, excessive
      sub-technique specificity, abstention quality, and invented IDs.
- [ ] Confirm no technique mapping is based solely on a country/company label,
      an IP address, an alert title, or an upstream hypothesis.
- [ ] Repeat selected cases to assess consistency.
- [ ] Compare latency, model failures, and analyst usefulness with the baseline.
- [ ] Save inputs, expected results, catalog/model configuration, outputs, and
      reviewer decisions in a fresh evaluation directory under the owning agent.

### Minimum acceptance conditions

1. All emitted new technique IDs exist and are active in the selected catalog.
2. Every proposed mapping has valid incident evidence references and an
   analyst-reviewable rationale; reviewers assess whether the evidence entails it.
3. Insufficient evidence produces an explicit abstention rather than forced mapping.
4. Retrieval/model failures remain distinguishable from an evidence-based abstention.
5. Upstream provenance, partial status, and historical limitations are preserved.
6. Analyst-agreed quality and performance thresholds are met on the test set.
7. Baseline regression checks pass.

The small test set is POC evidence, not a production accuracy benchmark.

## 6. Hosted acceptance and later adoption

- [ ] Approve and publish the isolated candidate; verify the catalog version/hash
      in hosted outputs matches the tested asset.
- [ ] Run the same evaluation inputs through the hosted experiment.
- [ ] Decide whether catalog retrieval stays in Recommendation or moves into
      Enrichment based on reuse needs, compatibility, and measured performance.
- [ ] Approve any cross-agent handoff changes and full-chain integration.
- [ ] Test Triage → Enrichment → Recommendation and verify exported JSON and reports.
- [ ] Record rollback steps and retain baseline evidence.
- [ ] After acceptance, consolidate into the maintained agent implementation;
      archive the experiment's evidence and avoid two drifting implementations.

## Maintenance checklist

- [ ] Assign ownership for catalog updates.
- [ ] For each adopted release, retain the new snapshot/checksum, rebuild the
      index, review changed/revoked techniques, and rerun mapping evaluations.
- [ ] Record the catalog version in every result for reproducibility.
- [ ] Do not silently replace a deployed snapshot with the repository's moving
      latest-version file.

## First actions when resuming

1. Select the versioned Enterprise ATT&CK JSON snapshot.
2. Gather the 10–15 evaluation incidents and analyst-expected results.
3. Confirm POC ownership and the separate test deployment target.
4. Finalize retrieval/output contracts, then implement and evaluate.

## References

- [Official ATT&CK data and tools](https://attack.mitre.org/resources/attack-data-and-tools/)
- [Official STIX 2.1 repository](https://github.com/mitre-attack/attack-stix-data)
- [Triage handoff and known omissions](../triage_agent/INDICATOR_CONTRACT.md)
- [Review and Appendix C](../triage_agent/CODE_REVIEW_2026-11-06.md)
- [Current Enrichment scope](README.md)
- [Recommendation input/output contract](../recommendation_agent/CONTRACT.md)
