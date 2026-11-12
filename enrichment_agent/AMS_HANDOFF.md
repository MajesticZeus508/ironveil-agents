# AMS receiver and sequential handoff

Current live staging recheck: Enrichment **0.1.3 active/latest**; automated
Triage → Enrichment → Recommendation exercised successfully by the operator.
The entry owns submission/collection, receipt checks and attachment projection.
See [current runbook](../DEMO.md). Original receiver verification below is historical.

## Implemented now

- Separate pod source in `ams/`, scaffold-owned pins: Agent Kit 0.50.0,
  sling-agent 0.1.0.dev6 and ripgrep-bin 15.2.0.
- Deterministic file-first processing, no model inference required for lookup
  planning or status. The scaffold's configured model is `openai/gpt-5.4`; the
  gateway accepted its streaming/system/tool request shape.
- Strict Harness dispatch input with one explicit managed file in `sources`.
  Each fresh request resets attachment state, including requests without a file.
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

## Input contract for the Triage caller

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

The placeholder is documentation only. The implemented Triage caller uses its
current invocation's confirmed export ID to invoke this separate deployed
Enrichment agent only after export succeeds. The invoking user needs access to
both agents and the file. Never pass a local path or model-rewritten file content.
The receiver does not invoke Triage or Recommendation itself.

## Original receiver verification and remaining limits

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
