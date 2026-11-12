"""Managed-file receiver: deterministic AWS-pending results, no hidden fixtures."""
import json
from typing import Annotated

if __package__:
    from .contracts import ContractError, parse_bytes
    from .enrich import enrich, render_report
    from .history import UnconfiguredAWSHistory
else:
    from contracts import ContractError, parse_bytes
    from enrich import enrich, render_report
    from history import UnconfiguredAWSHistory

INPUT_LIMIT = 10_000_000
OUTPUT_LIMIT = 24_000_000


async def process_uploaded(file_ids, store):
    """Read exactly the explicitly supplied ID; never list files or use local paths."""
    if not isinstance(file_ids, list) or len(file_ids) != 1:
        return {"error": "missing_handoff", "message": "Supply exactly one extracted_indicators.json file reference."}
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
        result = enrich(handoff, UnconfiguredAWSHistory(), handoff_sha256=digest)
    except ContractError:
        return {"error": "invalid_handoff", "message": "Handoff failed alert-indicators/3 validation; no export performed."}
    result["handoff_receipt"] = {"file_id": file_id, "sha256": digest, "schema": "alert-indicators/3"}
    documents = [
        ("enrichment_results.json", json.dumps(result, separators=(",", ":"), ensure_ascii=True, allow_nan=False) + "\n", "application/json"),
        ("enrichment_report.md", render_report(result), "text/markdown"),
    ]
    if any(len(content.encode("utf-8")) > OUTPUT_LIMIT for _, content, _ in documents):
        return {"error": "output_too_large", "message": "Result exceeds managed export limit; no truncated export was created."}
    exports = []
    for filename, content, mime in documents:
        item = {"filename": filename, "mime_type": mime, "status": "unconfirmed"}
        try:
            written = await store.write_file(filename, content, mime_type=mime)
            body = getattr(written, "body", None)
            if (isinstance(getattr(written, "status", None), int) and 200 <= written.status < 300
                    and isinstance(body, dict) and isinstance(body.get("id"), str) and body["id"].strip()):
                item.update(status="created", file_id=body["id"])
        except Exception:
            pass  # Never retry uncertain additive writes or persist provider errors.
        exports.append(item)
        if item["status"] != "created":
            break
    return {"run": result["run"], "handoff_receipt": result["handoff_receipt"],
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
        """Validate the one current-request triage file and export AWS-pending enrichment results."""
        from spark_agent_kit import SGPResourceClient
        state = runtime.state if runtime is not None else {}
        ids = state.get("source_file_ids", []) if isinstance(state, dict) else getattr(state, "source_file_ids", [])
        output = await process_uploaded(ids, SGPResourceClient())
        return json.dumps(output, allow_nan=False), {"exports": output.get("exports", [])}

    return StructuredTool.from_function(coroutine=run_enrichment, name="run_enrichment",
        description=run_enrichment.__doc__, response_format="content_and_artifact")
