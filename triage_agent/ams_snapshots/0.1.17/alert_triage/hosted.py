"""Read only invocation-attached managed files; never local paths or model IDs."""
from typing import Annotated

if __package__:
    from .agent import LiveContextClient
    from .triage import analyze
    from .export import save_indicator_export
else:
    from agent import LiveContextClient
    from triage import analyze
    from export import save_indicator_export


async def analyze_uploaded(file_ids, reader, client, progress=None):
    if not file_ids:
        return {"error": "missing_upload", "message": "Attach a JSON or JSONL findings file. No bundled data is available."}
    if len(file_ids) != 1:
        return {"error": "file_count", "message": "Attach exactly one findings file per request."}
    file_id = file_ids[0]
    if progress:
        progress("Reading the uploaded findings…")
    try:
        result = await reader.read_file_bytes(file_id, max_bytes=1_000_000)
    except Exception:
        return {"error": "file_service_unavailable", "message": "Uploaded file could not be read. Check platform file access and retry."}
    if not isinstance(getattr(result, "body", None), bytes):
        return {"error": "file_read_failed", "status": getattr(result, "status", None),
                "message": "File content unavailable or over size limit. Check attachment access; no analysis was fabricated."}
    raw = result.body
    if len(raw) > 1_000_000:
        return {"error": "file_size", "message": "Upload exceeds 1 MB; it was refused, not truncated."}
    try:
        content = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return {"error": "encoding", "message": "Upload must be UTF-8 JSON or JSONL, not a binary document."}
    results = await analyze(content, client, progress=progress)
    results["run"]["input_file_id"] = file_id
    results["run"]["input_bytes"] = len(raw)
    if progress:
        progress("Preparing the indicator file…")
    exported = await save_indicator_export(results, reader)
    if progress and exported.get("status") != "created":
        progress("File creation failed or is unconfirmed; no attachment is claimed.")
    # Only compact status is returned to chat; the JSON file is the deliverable.
    return {"run": results["run"], "indicator_export": exported}


def status_message(output):
    """Code-generated status only; never include raw uploaded or model strings."""
    if "error" in output:
        return output["error"] + ": " + output["message"]
    run, export = output["run"], output["indicator_export"]
    counts = (f"{run['accepted_findings']} accepted findings; {run['incident_groups']} groups; "
              f"{run['completed']} context analyses completed; {run['failed']} failed; "
              f"{len(run['errors'])} input errors. Run: {run['status']}.")
    if export.get("status") == "created":
        return "Created extracted_indicators.json (" + export.get("schema", "alert-indicators/3") + "). " + counts
    return ("Export failed or unconfirmed; no attachment is claimed. " + counts +
            " No automatic retry; file creation may have occurred.")


def make_triage_tool(workdir):
    from langchain.tools import ToolRuntime
    from langchain_core.tools import InjectedToolArg
    from langchain_core.tools import StructuredTool
    import json
    async def run_triage(*, runtime: Annotated[ToolRuntime | None, InjectedToolArg] = None) -> tuple:
        """Read and triage the one user-uploaded JSON/JSONL file attached to this invocation.

        No model-supplied paths, content or file IDs. Missing uploads produce an error.
        Returns compact run status and a confirmed JSON attachment when stored.
        """
        from spark_agent_kit import SGPResourceClient
        from spark_agent_kit.api_contracts.harness.output.writer import SparkEventWriter
        if __package__:
            from .progress import TriageProgress
        else:
            from progress import TriageProgress
        state = runtime.state if runtime is not None else {}
        ids = state.get("source_file_ids", []) if isinstance(state, dict) else getattr(state, "source_file_ids", [])
        progress = TriageProgress(runtime.tool_call_id, SparkEventWriter()) if runtime is not None else None
        output = await analyze_uploaded(ids, SGPResourceClient(), LiveContextClient(), progress=progress)
        if progress and "error" in output:
            progress("Input unavailable or unsupported; no analysis performed.")
        return json.dumps(output, allow_nan=False), {"indicator_export": output.get("indicator_export", {}),
            "triage_progress": progress.artifact() if progress else {"text": ""}}
    return StructuredTool.from_function(coroutine=run_triage, name="run_triage",
        description=run_triage.__doc__, response_format="content_and_artifact")
