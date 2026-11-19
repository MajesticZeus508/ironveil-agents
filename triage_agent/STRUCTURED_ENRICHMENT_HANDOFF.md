# Structured Triage → Enrichment caller (2026-11-17)

> **Historical implementation checkpoint.** The full structured chain was later
> deployed as 0.1.29 / 0.1.4 / 0.1.8; diagnostics followed as 0.1.30 / 0.1.5 /
> 0.1.9. Use [WORKFLOW.md](WORKFLOW.md) for the current contract and
> [diagnostic release](DIAGNOSTIC_RELEASE_2026_11_18.md) for storage findings.
> “Unpublished,” “blocked” and step 7's file requirement below describe the
> earlier caller-only phase, not today's structured workflow.

**Superseding follow-up:** full Enrichment → Reporting structured forwarding is
now implemented/tested too. The managed-file gate described in step 7 below is
retained only for legacy explicit file tickets; current structured runs verify
the code-owned output envelope and forward it without intermediate reads.
See [completion/release ledger](STRUCTURED_CHAIN_RELEASE_2026_11_17.md) for
SDK success and blocked receiver publication. No new version became active.

**Local, unpublished implementation.** Changes are in editable
`plugins/alert_triage/` (Dev targets retained), tests and this directory's docs.
No retained release/snapshot, receiver, Recommendation source, agent ID, model,
dependency pin, Events rule or deployed version was changed in this caller pass.
Triage 0.1.28 remains unchanged. Publication requires separate approval.

## Transport and stage policy

1. Analyze the current explicit file/LUX input as before. Zero accepted findings
   cannot submit. Extraction-only/deferred narrative, partial errors, unknown
   entity/null values, supplied labels and original provenance remain unchanged.
2. Build v3 once using `build_indicator_export`. `prepare_handoff` snapshots the
   object and computes `canonical-json/1` before the existing single managed
   Triage export attempt. Export success/failure is independent of handoff readiness.
3. `run_triage` returns `enrichment_handoff` with the original v3 object under
   `handoff`, `status="ready"`, `file_id=null`, `schema="alert-indicators/3"`,
   `input_mode="structured"`, `canonicalization="canonical-json/1"`, and equal
   `sha256`/`payload_sha256`. It is persisted in that turn's code-owned tool
   result for the next checkpoint-sized stage, not a new top-level output channel.
   This increases stored tool-result size; data-marking/retention controls still
   apply. There is no model reconstruction or content readback from file storage.
4. `submit_enrichment` reads only the current turn's `run_triage` result (after
   the latest human boundary), revalidates/recomputes the hash and submits once.
   It does not gate on `indicator_export.status`, look up filenames, recover old
   payloads, automatically fall back to file mode or retry a rejected form.
5. The submission ticket retains only hash/mode/schema metadata plus actual
   child IDs, not another payload copy. Enrichment collection accepts the null
   input file ID **only** for an explicitly structured, internally consistent
   ticket. Legacy file tickets remain verifiable for read-only reconciliation;
   new Enrichment submissions use the form only.
6. Before projecting any child attachment, verify all six receipt fields:
   schema, input mode, canonicalization, explicit null file ID, and both digests.
   Missing fields, legacy/downgraded receipts or mismatches fail closed without
   retry. Confirmed exports must still agree with action-scoped Harness FileBlocks.
7. Before Recommendation, the existing managed Enrichment JSON is read and its
   receipt must equal the verified child receipt and structured ticket. Its exact
   file-byte hash is then sent to Recommendation using the existing file channel.
   No confirmed/readable Enrichment JSON means **no Recommendation submission**.

The five-stage workflow, submission/collection budgets, bounded read-only GET
retry policy and no submission/write/model retry policy remain. Fresh requests
are independent; no content cache, shared client/config or automatic checkpoint
replay/exactly-once guarantee is added. Uncertain submissions retain acknowledged
IDs and require reconciliation. Unconfirmed writes do not become FileBlocks.
Final status reports downstream status even if the Triage export was unconfirmed.

## Exact outgoing graph envelope

`handoff` below is the **object**, not a JSON string or original LUX finding:

```python
{
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

No file part accompanies it. `AMSRemoteAgent` receives that graph input; its
invocation body wraps it once under `input`. There are no application-supplied
credentials or parent continuation IDs. SDK docs say “build a fresh config to
start a new conversation”; this implementation retains a fresh client and
`{"configurable": {}}` per submission.
[AMSRemoteAgent, 0.50.0](https://scaleapi.github.io/spark-agent-kit/reference/agents/#spark_agent_kit.agents.remote.ams.ams_remote_agent.AMSRemoteAgent)
was checked against pinned
`v0.50.0:src/spark_agent_kit/agents/remote/ams/ams_remote_agent.py`.
No SDK calls or dependency internals were changed.

Canonical digest: SHA-256 over ASCII bytes of
`json.dumps(handoff, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
allow_nan=False)` with no newline. Not RFC 8785; arrays retain order, all keys
including unknown fields participate, and no values are normalized/coerced.
Producer bounds match the receiver's structured transport: 10,000,000 serialized
bytes, depth 40, string/key length 10,000, 1,000,000 visited values/keys, 1,000
incidents and 10,000 observations. The receiver remains authoritative for full
v3 joins/refs/field validation; producer checks do not claim semantic fact-checking.
See [receiver envelope and receipt contract](../enrichment_agent/AMS_HANDOFF.md#structured-input-local-unpublished).

## Verification and release gates

Baseline ordinary CLI: **73 discovered, 55 passed, 18 skipped**.
Final ordinary CLI: **81 discovered, 61 passed, 20 skipped** (Agent Kit/httpx
absent). Enrichment regression: **34 discovered, 30 passed, four SDK skips**;
`prepare_pod.py --check` and workspace `git diff --check` passed. No new
scaffold, managed probe, package check or hosted invocation was run in this
offline caller pass; previous release evidence does not certify these bytes.
Local tests exercise exact form/hash/snapshot behavior; unknown/null preservation;
malformed/nonfinite/oversized inputs; no file-mode fallback; receipt downgrade,
missing-field and mismatch rejection; uncertain submissions without retries;
independent requests; and a real LUX → Triage → actual Enrichment processing
integration using stub stores with the Triage intermediate write deliberately
unconfirmed. No live submission, history/model call or real managed file storage
is involved. History remains `not_configured`, partial with unknown counts; no
response actions are executed.

SDK wire-roundtrip and graph/checkpointer tests are included, but ordinary CLI
skips them when Agent Kit/httpx are absent. Their execution, representative raw
Harness hosted acceptance, packaging/security checks and operator publication
approval remain release gates. Deploy/verify the matching Enrichment receiver
before the caller in each intended environment; never direct the new caller to
an old file-only receiver and silently downgrade. Existing editable IDs target
Dev, while the receiver implementation directory has staging release history;
review target mapping explicitly before any release.

**This removes only the Triage → Enrichment intermediate-file dependency.**
Triage's export is still attempted once, Enrichment/Recommendation outputs still
depend on managed storage, and final-report storage is not established fixed.
