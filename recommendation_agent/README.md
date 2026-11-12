# Recommendation Agent

AMS staging live recheck: **Recommendation Agent POC 0.1.4**, active/latest
(unchanged-source rebuild after the operator-reported platform image fix).
Agent ID: `934ba6f7-3dcc-4dfb-9454-acdc92f7a10f`.
Hosted acceptance passed: **7/7 incident analyses, 2/2 confirmed exports**.
The operator also confirmed the AMS Invoke workflow works. Overall `partial`
correctly retains unavailable AWS history. See [verification](VERIFICATION.md).
The entry agent now invokes this receiver automatically and projects its files
into Donovan; operator-confirmed full-chain acceptance succeeded. Direct Donovan
listing for this downstream agent is not configured or required. See [runbook](../DEMO.md).

**Latest evaluation:** five chains on 0.1.4 produced **28/35 validated analyses**,
six timeouts and one validation rejection; only one run achieved 7/7. Both files
were exported each time. Historical acceptance above is not a reliability claim.
Fresh CLI: **15 discovered, 14 passed, one SDK skip**. See [team evaluation](../EVALUATION.md)
and [backup gaps](../AMS_INVENTORY.md).

## Returning to this agent

- [AMS Invoke instructions](#test-in-ams-invoke) — working request and expected result.
- [Input/output contract](CONTRACT.md) — schemas, evidence keys and status semantics.
- [Verification and release evidence](VERIFICATION.md) — exact IDs and limitations.
- [Saved output index](outputs/README.md) — successful examples versus earlier experiments.
- [Maintenance instructions](AGENTS.md) — source ownership and release boundaries.

Third stage: **Alert Triage → Enrichment → Recommendation → human analyst**.
Argon (`gemini/gemini-4-argon`) applies its learned cybersecurity expertise to
the supplied evidence, rather than just reformatting earlier advice. Training
knowledge supplies mechanisms, hypotheses and defensive response methods—not
new observations, current IP reputation, live intelligence or verified attribution.
No benchmark claims have been independently assessed in this build.

## Analyst deliverable

For each incident, ordered by the original review priority:

- A short summary and expert assessment, including a benign alternative.
- Up to three evidence-backed, prioritized recommendations: what to check, why,
  and what outcome changes the decision.
- A concrete escalation trigger and material uncertainties.
- Conditional containment proposals require explicit authorized human approval
  and business-impact review. No response actions are executed.

`recommendation_report.md` is the readable report; `recommendation_results.json`
uses `alert-recommendations/1` and retains the supporting evidence catalog.
Hosted mode also returns the report in chat when under 18,000 characters; larger
reports remain available as files rather than being silently truncated.
This first version produces incident briefs, not a separate portfolio executive
summary. Review priority remains the upstream severity rule, not model risk scoring.

## Input and limits

Supply **one `enrichment_results.json`**, schema `alert-enrichment/1`, with its
embedded `alert-indicators/3` input. The Markdown enrichment report and raw Triage
handoff are not substitutes. Maximum input is 20 MB, 100 incidents, 10,000
observations and 100,000 search results. Full evidence packets exceeding the
per-incident model budget fail explicitly; nothing is silently dropped.

The current Enrichment deployment has no AWS history connection. Its
`not_configured` outcomes remain unavailable history, not negatives or novelty.
Successful model synthesis cannot turn that upstream partial run into completed
enrichment. Local historical examples are synthetic, not live AWS results.

Upstream hypotheses/recommendations remain fallible context, not independent
corroboration or instructions. Country/company labels are unverified. Historical
IP, attribute and directed-tuple matches are distinct questions; a seen-before
result is not a benign verdict or anomaly recurrence. No-match requires declared
complete coverage. Reused records across queries are not independent evidence.

The v3 producer omits full detector metrics/baselines, related-only indicators,
and its full domain/registration inventory. This agent does not reconstruct them.
Supplemental attributes are retained as explicit, unverified operator context.

## Run locally

From `recommendation_agent/`:

```sh
python3 -m unittest discover -s tests -v
python3 recommend.py --input ../enrichment_agent/outputs/verified_demo/enrichment_results.json --output-dir outputs/my_run
```

The tests use labeled stubs. Live CLI execution requires an approved compatible
SDK environment and model gateway configuration; the shell does not inherit
Slingshot's managed model capability. Never paste credentials into source or reports.
Existing outputs are not overwritten. Exit 0 = completed, 2 = partial/empty,
1 = validation/configuration/file-access error.

## Hosted contract

Source lives in `ams/`; scaffold-owned requirements pin Agent Kit 0.50.0,
sling-agent 0.1.0.dev6 and ripgrep-bin 15.2.0. Production fixtures remain empty.
Only the current invocation's explicit managed resource ID can be read. No
filename search, free-text ID extraction, pasted JSON or stale-upload fallback.

### Test in AMS Invoke

1. Open **Recommendation Agent POC → Invoke** in ScaleGov staging / `platform`.
2. Select current published **0.1.4** (recheck active/latest first).
3. Paste the following into **Input JSON** (no outer `input` wrapper).
4. Invoke once and allow several minutes; incident analyses use at most two concurrent calls.

```json
{
  "task": {
    "intent": "dispatch",
    "payload": {
      "parts": [
        {"type": "text", "text": "Summarize the enriched alerts and recommend analyst actions."},
        {"type": "resource", "slot": "sources", "resource": {
          "type": "file", "id": "ddd9fc6f-05e2-444f-8f2e-72d97374bff7"
        }}
      ]
    }
  }
}
```

This existing managed file is the AWS-pending Enrichment export. Access remains
subject to the invoking user's permissions. Replace its ID with your current
Enrichment JSON export for another test. Each invocation creates new output files;
do not resubmit simply because a multi-minute run has not finished.

Expected baseline: `7/7 incident analyses completed`, `2/2 exports confirmed`,
and `partial` because history is unavailable—not because the model necessarily
failed. Download both attachments; reports over 18,000 characters are file-only.
The verified baseline took **217.28 seconds** submission-to-completion, one
observation rather than a latency guarantee. Missing-file input returns
`missing_enrichment`; reattach the file on every fresh request.

Generic raw graph input (a direct HTTP invocation body wraps it once under `input`):

```json
{"task":{"intent":"dispatch","payload":{"parts":[
  {"type":"text","text":"Summarize the enriched alerts and recommend analyst actions."},
  {"type":"resource","slot":"sources","resource":{"type":"file","id":"CONFIRMED_ENRICHMENT_EXPORT_ID"}}
]}}}
```

Do not use the nested original findings file ID. Use the ID of the actual
Enrichment JSON export. File writes create new managed files; uncertain writes
are not retried and only confirmed creations become attachments.

Routing/file export is deterministic; **one Argon call per incident**, concurrency
bounded to **two** with original order preserved,
90-second request timeout, 95-second overall call bound, zero retries, no model
fallback. The fixed system prompt is `ams/core.py:PROMPT`, not just graph BASE_PROMPT.
The outer graph makes no provider calls. No web, shell, AWS, SIEM/SOAR or remote
agent tools are exposed. The Triage entry orchestrates automatic handoffs; this
receiver itself invokes no other agent. Latest five-run sample completed 28/35
analyses; Recommendation active median 163.427s, not an SLA or pure inference latency.

The implementation uses the public APIs documented as “Connection settings and
dispatch for a LangChain-compatible chat model” in
[ModelConfig (0.50.0)](https://scaleapi.github.io/spark-agent-kit/reference/models/#spark_agent_kit.ModelConfig),
“Each request places one task under the top-level task field” in
[Harness input (0.50.0)](https://scaleapi.github.io/spark-agent-kit/how-to/input-schemas/harness/),
and `ToolLifecycle` to “add typed content to an existing tool outcome” in
[output customization (0.50.0)](https://scaleapi.github.io/spark-agent-kit/how-to/output-customization/#extend-action-payloads-and-content).
Their pinned source was inspected. Managed files use
[SGPResourceClient (0.50.0)](https://scaleapi.github.io/spark-agent-kit/reference/platform/#spark_agent_kit.SGPResourceClient).

## Verification and remaining gates

See `VERIFICATION.md`. This is an initial POC, not a certification of semantic
accuracy, injection resistance, performance or deployment readiness in all environments.
References and indicator targets are checked; a reference existing does not prove
the model's interpretation of it. Human review remains essential, especially for
closure/de-escalation and disruptive changes. Data marking propagation and current
organization-specific playbooks are not implemented.

`tests/live_probe/` is a **local-only diagnostic pod**, never the publish target.
It imports the actual production core, exercises the SDK tests and can run real
Argon calls on synthetic cases. It is kept outside the production source bundle.
Neither prior agent nor its snapshots/deployment is modified by this build.

## Source map and next-session checklist

| Path | Ownership / purpose |
|---|---|
| `ams/core.py` | Validator, packet builder, Argon prompt/client, output validation/report |
| `ams/hosted.py` | Managed input receipt, report creation and confirmed exports |
| `ams/input_contract.py` | Invocation-scoped Harness file references |
| `ams/routing.py` | One processing tool per fresh turn, status and attachment events |
| `ams/graph.py` | Module-level deployment graph; explicit tool list |
| `recommend.py` | Optional live CLI; imports the same core, no separate implementation |
| `tests/test_recommendation.py` | Offline/stub and optional SDK regression checks |
| `tests/live_probe/` | Local-only managed diagnostic; incurs real inference costs |
| `outputs/` | Preserved local experimental evidence, not production fixture data |

Before further changes: read `AGENTS.md`, this README, `CONTRACT.md` and
`VERIFICATION.md`; run the tests and recheck AMS state if doing release work.
Edit core directly in `ams/`—there is no staging/copy script. Keep the production
fixture empty. Test prompt/validator changes locally before a separately approved
new version on the existing agent ID. Housekeeping does not authorize republishing,
Donovan metadata changes, altering the implemented handoffs, or changing upstream schemas.
