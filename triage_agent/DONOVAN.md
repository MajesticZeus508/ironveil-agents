# Donovan operator handoff

## Current target

- **Network Investigation Demo**, ScaleGov staging, tenant `6a1099f9e1ca37ee1216d8c3`.
- Agent `d4ffbfc9-696f-4a5a-b174-75daaa1c993f`.
- Latest active published release at live recheck: **0.1.24**, staging polling-fix
  promotion. See [current runbook](../DEMO.md) for full-chain IDs and security caveats.
- Discovery tag `ps:donovan:chat` was configured and verified earlier in the session.

## Run

Start a new chat, select the agent, attach one UTF-8 JSON/JSONL findings file
(1 MB / 100 records), and send:

> Run the network investigation and produce analyst recommendations.

The local example is `staging_input_verification.json` (hash-verified original
run2 JSONL bytes; the former filename is absent). If a picker
rejects `.jsonl`, rename a copy to `.json`. No fixture is deployed, no pasted-data
fallback exists, and previous attachments are not silently reused.

Expect stage results and final status in Thinking, with confirmed attachments.
Triage defaults to extraction only; Recommendation supplies incident narrative.
Failures remain explicit. The operator confirmed the full-chain presentation works;
the builder did not independently interact with a browser. These are code-generated
status updates, not exposed private reasoning.

The final result is five managed attachments: `extracted_indicators.json`
(`alert-indicators/3`), Enrichment JSON/Markdown and Recommendation JSON/Markdown.
Open `recommendation_report.md` for analyst advice. File writes create new files,
even if names match. Enrichment plans history criteria but executes no AWS searches.
No autonomous response action is performed.

## Interpret failures

- Missing/unreadable upload: explicit error, no sample fallback or invented analysis.
- Invalid records: errors retained; valid records continue.
- Context timeout/invalid response: extracted observations retained, incident context
  unavailable, final run partial. Export may still succeed.
- File write uncertain/failed: no attachment claimed and no automatic write retry.
- A completed AMS invocation is not proof that every incident's context succeeded.
- `narrative_deferred` is intentional in default Triage mode, not lost extraction.
- Downstream failure: **INVESTIGATION INCOMPLETE**, prior files retained; reconcile
  recorded child IDs before retrying. There is no automatic submission retry.

For the main fixture: **17 findings, seven groups, 98 observations**. These are
different counts, not interchangeable alert or unique-IP counts.

## Direct invocation input

Graph input:

```json
{
  "task": {
    "intent": "dispatch",
    "payload": {
      "parts": [
        {"type": "text", "text": "Extract indicators and create the handoff JSON."},
        {"type": "resource", "slot": "sources", "resource": {"type": "file", "id": "<authorized-upload-id>"}}
      ]
    }
  }
}
```

AMS HTTP invocation wraps that object **once** under `input`. Do not send plain
`messages`. Public stored output is `messages` and `render_events`, including
tool/dispatch outcomes, the saved thinking block, and confirmed file block.
Current-request source IDs are application-controlled, not chosen by the model.

## Verification evidence

Latest evaluation: five chains/five files each, 28/35 validated analyses, six
timeouts and one validation rejection; see [team summary](../EVALUATION.md).
Historical operator-confirmed full chain: `inv_b394de1e-5e49-4616-8495-f936041f9844`,
206.181s end-to-end, 7/7 recommendations, five confirmed file blocks. Historical
standalone presentation evidence follows; it does not describe current stage routing.

- 0.1.15: 19 live text deltas delivered over SSE; exact durable-log match; successful
  17/7/98 run. This precedes the thinking-block presentation change.
- 0.1.16: stored thinking block with paragraph spacing and no timestamps verified,
  confirmed file `4d9933ea-0354-4022-a818-7572219adce6`; five contexts passed and two
  timed out. Invocation `inv_0ed6c7bf-c868-4f73-b74b-44a15992c0f0`, thread
  `390351f6-d42f-493d-97c7-e80124c1994a`.
- Operator subsequently reported that the revised UI works well.
- 0.1.17: active/latest status and published-source equality verified; no new live
  inference run was launched during documentation cleanup.

Reference Donovan routes `thinking` fragments to thinking content and drops numeric
`progress` events. Do not use a generic JSON request tool to read an endless SSE
endpoint: it waits for closure. Poll the finite invocation/status/output APIs for
verification instead. The managed local probe still sends a legacy messages input;
its pre-inference rejection does not invalidate the hosted Harness tests.

Older bundled-fixture, pasted-input, no-download, and v1/v2-only guidance is
historical; see SESSION_HISTORY.md and BUILD_STATUS.md rather than following it.
