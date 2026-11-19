"""Current-request managed-file input, confirmed exports and concise chat report."""
import json
import hashlib
from typing import Annotated

if __package__:
    from .core import ArgonClient, LIMIT, ValidationError, parse, recommend, render_report
    from .structured_input import canonical_payload
    from .file_writes import write_once
else:
    from core import ArgonClient, LIMIT, ValidationError, parse, recommend, render_report
    from structured_input import canonical_payload
    from file_writes import write_once


async def process_uploaded(ids, store, client=None):
    return await process_input(ids, None, store, client)


async def process_input(ids, enrichment, store, client=None):
    """No prose parsing, stale input, automatic fallback or additive retries."""
    if not isinstance(ids, list):
        return {"error": "invalid_input_mode", "message": "File references must be a list."}
    if enrichment is not None:
        if ids:
            return {"error": "ambiguous_enrichment", "message": "Supply a file or enrichment form, not both."}
        try:
            data, digest = canonical_payload(enrichment)
        except ValidationError:
            return {"error": "invalid_enrichment", "message": "Structured input failed bounded alert-enrichment/1 validation; no analysis or export performed."}
        return await process_data(data, digest, None, digest, "structured", store, client)
    if not isinstance(ids, list) or len(ids) != 1:
        return {"error": "missing_enrichment", "message": "Attach exactly one enrichment_results.json (alert-enrichment/1). No previous upload is reused."}
    if not isinstance(ids[0], str) or not ids[0].strip() or len(ids[0]) > 256 or any(ord(c) < 32 for c in ids[0]):
        return {"error": "invalid_file_id", "message": "Supply a valid managed file reference."}
    try:
        response = await store.read_file_bytes(ids[0], max_bytes=LIMIT)
        if not (type(getattr(response, "status", None)) is int and 200 <= response.status < 300 and isinstance(response.body, bytes)):
            return {"error": "file_read_failed", "message": "Enrichment file unavailable, inaccessible or oversized. No fallback used."}
    except Exception:
        return {"error": "file_read_failed", "message": "Enrichment file could not be read. No fallback used."}
    try:
        data, digest = parse(response.body)
        # Preserve existing UTF-8 file byte limits rather than imposing the
        # structured channel's ASCII-escaped serialization limit on files.
        payload_digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
            ensure_ascii=True, allow_nan=False).encode("ascii")).hexdigest()
    except ValidationError:
        return {"error": "invalid_enrichment", "message": "Input failed alert-enrichment/1 validation; no analysis or export performed."}
    return await process_data(data, digest, ids[0], payload_digest, "file", store, client)


async def process_data(data, digest, file_id, payload_digest, mode, store, client):
    receipt = {"schema": "alert-enrichment/1", "input_mode": mode, "file_id": file_id,
               "sha256": digest, "payload_sha256": payload_digest, "canonicalization": "canonical-json/1"}
    try:
        result = await recommend(data, client or ArgonClient(), digest)
    except ValidationError:
        return {"error": "invalid_enrichment", "message": "Input failed alert-enrichment/1 validation; no analysis or export performed."}
    report = render_report(result)
    documents = [("recommendation_results.json", json.dumps(result, separators=(",", ":"), ensure_ascii=True, allow_nan=False), "application/json"),
                 ("recommendation_report.md", report, "text/markdown")]
    if any(len(content.encode()) > 24_000_000 for _, content, _ in documents):
        return {"error": "output_too_large", "message": "Result exceeds export limit; no truncated export created."}
    exports = []
    for filename, content, mime in documents:
        item = {"filename": filename, "mime_type": mime, "status": "unconfirmed"}
        created_id, failure = await write_once(store, filename, content, mime)
        if failure is None:
            item.update(status="created", file_id=created_id)
        else:
            item["write_diagnostic"] = failure
        exports.append(item)
        if item["status"] != "created":
            break
    return {"run": result["run"], "source_sha256": digest, "received_file_id": file_id,
            "export_diagnostics": [e["write_diagnostic"] for e in exports if "write_diagnostic" in e],
            "handoff_receipt": receipt,
            "exports": exports, "report": report if len(report) <= 18000 else None,
            "export_status": "completed" if len(exports) == 2 and all(x["status"] == "created" for x in exports) else "partial"}


def status_message(output):
    if "error" in output:
        return output["error"] + ": " + output["message"]
    count = sum(x["status"] == "created" for x in output["exports"])
    status = f"Recommendation run: {output['run']['status']}; {output['run']['completed']}/{output['run']['incident_count']} incident analyses completed. {count}/2 exports confirmed. No actions executed."
    if count != 2:
        status += " Unconfirmed writes are not retried automatically."
    return status + ("\n\n" + output["report"] if output.get("report") else " Download the report for the full analyst summary.")


def make_recommendation_tool():
    from langchain.tools import ToolRuntime
    from langchain_core.tools import InjectedToolArg, StructuredTool

    async def run_recommendation(*, runtime: Annotated[ToolRuntime | None, InjectedToolArg] = None) -> tuple:
        """Analyze one current-request enrichment handoff with Argon; export human-reviewed recommendations."""
        from spark_agent_kit import SGPResourceClient
        state = runtime.state if runtime is not None else {}
        ids = state.get("source_file_ids", []) if isinstance(state, dict) else getattr(state, "source_file_ids", [])
        data = state.get("structured_enrichment") if isinstance(state, dict) else getattr(state, "structured_enrichment", None)
        output = await process_input(ids, data, SGPResourceClient())
        return json.dumps(output, allow_nan=False), {"exports": output.get("exports", [])}

    return StructuredTool.from_function(coroutine=run_recommendation, name="run_recommendation",
        description=run_recommendation.__doc__, response_format="content_and_artifact")
