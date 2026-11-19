"""Explicit file/form receiver: deterministic AWS-pending results, no fallback."""
import json
from typing import Annotated

if __package__:
    from .contracts import ContractError, canonical_handoff, identity, parse_bytes
    from .enrich import enrich, render_report
    from .history import UnconfiguredAWSHistory
    from .file_writes import write_once
else:
    from contracts import ContractError, canonical_handoff, identity, parse_bytes
    from enrich import enrich, render_report
    from history import UnconfiguredAWSHistory
    from file_writes import write_once

INPUT_LIMIT = 10_000_000
OUTPUT_LIMIT = 24_000_000


async def process_uploaded(file_ids, store):
    """Read exactly the explicitly supplied ID; never list files or use local paths."""
    return await process_input(file_ids, None, store)


async def process_input(file_ids, structured_handoff, store):
    """Select one explicit mode before any I/O; never retry or reuse prior input."""
    if not isinstance(file_ids, list):
        return {"error": "invalid_input_mode", "message": "File references must be a list."}
    if structured_handoff is not None:
        if file_ids:
            return {"error": "ambiguous_handoff", "message": "Supply a file or structured handoff, never both."}
        try:
            handoff, digest = canonical_handoff(structured_handoff, INPUT_LIMIT)
        except ContractError:
            return {"error": "invalid_handoff", "message": "Structured handoff failed bounded alert-indicators/3 validation; no export performed."}
        receipt = {"file_id": None, "sha256": digest, "schema": "alert-indicators/3",
                   "input_mode": "structured", "payload_sha256": digest,
                   "canonicalization": "canonical-json/1"}
        return await process_handoff(handoff, digest, receipt, store)
    if len(file_ids) != 1:
        return {"error": "missing_handoff", "message": "Supply exactly one handoff file reference or triage_handoff form."}
    file_id = file_ids[0]
    if not isinstance(file_id, str) or not file_id.strip() or len(file_id) > 256:
        return {"error": "invalid_file_id", "message": "A valid managed file reference is required."}
    try:
        response = await store.read_file_bytes(file_id, max_bytes=INPUT_LIMIT)
    except Exception:
        return {"error": "file_read_failed", "message": "Handoff file could not be read; no search or export performed."}
    if not (isinstance(getattr(response, "status", None), int) and 200 <= response.status < 300
            and isinstance(getattr(response, "body", None), bytes)):
        return {"error": "file_read_failed", "message": "Handoff file unavailable, inaccessible or oversized; no fallback used."}
    try:
        handoff, digest = parse_bytes(response.body, INPUT_LIMIT)
        # File bounds apply to received UTF-8 bytes, not an ASCII-escaped re-encoding.
        # Preserve existing file acceptance while using the same canonical hash.
        payload_digest = identity(handoff)
    except ContractError:
        return {"error": "invalid_handoff", "message": "Handoff failed alert-indicators/3 validation; no export performed."}
    receipt = {"file_id": file_id, "sha256": digest, "schema": "alert-indicators/3",
               "input_mode": "file", "payload_sha256": payload_digest,
               "canonicalization": "canonical-json/1"}
    return await process_handoff(handoff, digest, receipt, store)


async def process_handoff(handoff, digest, receipt, store):
    try:
        result = enrich(handoff, UnconfiguredAWSHistory(), handoff_sha256=digest)
    except ContractError:
        return {"error": "invalid_handoff", "message": "Handoff failed alert-indicators/3 validation; no export performed."}
    result["handoff_receipt"] = receipt
    structured_result = {"status": "ready", "schema": "alert-enrichment/1",
                         "canonicalization": "canonical-json/1",
                         "payload_sha256": identity(result), "payload": result}
    if len(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")) > 20_000_000:
        structured_result = {"status": "unavailable", "error": "structured_result_too_large"}
    documents = [
        ("enrichment_results.json", json.dumps(result, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", "application/json"),
        ("enrichment_report.md", render_report(result), "text/markdown"),
    ]
    if any(len(content.encode("utf-8")) > OUTPUT_LIMIT for _, content, _ in documents):
        return {"error": "output_too_large", "message": "Result exceeds managed export limit; no truncated export was created."}
    exports = []
    for filename, content, mime in documents:
        item = {"filename": filename, "mime_type": mime, "status": "unconfirmed"}
        file_id, failure = await write_once(store, filename, content, mime)
        if failure is None:
            item.update(status="created", file_id=file_id)
        else:
            item["write_diagnostic"] = failure
        exports.append(item)
        if item["status"] != "created":
            break
    return {"run": result["run"], "handoff_receipt": result["handoff_receipt"],
            "export_diagnostics": [e["write_diagnostic"] for e in exports if "write_diagnostic" in e],
            "structured_result": structured_result,
            "history_status": "not_configured", "exports": exports,
            "export_status": "completed" if len(exports) == 2 and all(e["status"] == "created" for e in exports) else "partial"}


def status_message(output):
    if "error" in output:
        return output["error"] + ": " + output["message"]
    created = sum(e["status"] == "created" for e in output["exports"])
    return (f"Validated triage handoff; {output['run']['query_count']} historical queries prepared. "
            "AWS historical data is not configured; no historical searches ran and no matches are claimed. "
            f"Run: {output['run']['status']}. {created}/2 output files confirmed. "
            + ("No automatic retry of unconfirmed writes." if created != 2 else ""))


def make_enrichment_tool():
    from langchain.tools import ToolRuntime
    from langchain_core.tools import InjectedToolArg, StructuredTool

    async def run_enrichment(*, runtime: Annotated[ToolRuntime | None, InjectedToolArg] = None) -> tuple:
        """Validate the current-request file or structured form and export AWS-pending results."""
        from spark_agent_kit import SGPResourceClient
        state = runtime.state if runtime is not None else {}
        ids = state.get("source_file_ids", []) if isinstance(state, dict) else getattr(state, "source_file_ids", [])
        handoff = state.get("structured_handoff") if isinstance(state, dict) else getattr(state, "structured_handoff", None)
        output = await process_input(ids, handoff, SGPResourceClient())
        return json.dumps(output, allow_nan=False), {"exports": output.get("exports", [])}

    return StructuredTool.from_function(coroutine=run_enrichment, name="run_enrichment",
        description=run_enrichment.__doc__, response_format="content_and_artifact")
