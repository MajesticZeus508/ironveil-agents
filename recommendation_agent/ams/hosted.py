"""Current-request managed-file input, confirmed exports and concise chat report."""
import json
from typing import Annotated

if __package__:
    from .core import ArgonClient, LIMIT, ValidationError, parse, recommend, render_report
else:
    from core import ArgonClient, LIMIT, ValidationError, parse, recommend, render_report


async def process_uploaded(ids, store, client=None):
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
        try:
            response = await store.write_file(filename, content, mime_type=mime)
            body = getattr(response, "body", None)
            if type(getattr(response, "status", None)) is int and 200 <= response.status < 300 and isinstance(body, dict) and isinstance(body.get("id"), str) and body["id"].strip():
                item.update(status="created", file_id=body["id"])
        except Exception:
            pass  # Additive write may have occurred; never automatically retry.
        exports.append(item)
        if item["status"] != "created":
            break
    return {"run": result["run"], "source_sha256": digest, "received_file_id": ids[0],
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
        output = await process_uploaded(ids, SGPResourceClient())
        return json.dumps(output, allow_nan=False), {"exports": output.get("exports", [])}

    return StructuredTool.from_function(coroutine=run_recommendation, name="run_recommendation",
        description=run_recommendation.__doc__, response_format="content_and_artifact")
