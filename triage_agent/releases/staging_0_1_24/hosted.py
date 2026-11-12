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


async def analyze_uploaded(file_ids, reader, client, progress=None, downstream=None, correlation=None, recommendation=None):
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
    if results["run"]["accepted_findings"] == 0:
        return {"error": "no_valid_findings", "message": "No valid swoop-ueba-finding/1 records. Attach original findings JSON/JSONL, not a handoff export. No downstream agents ran or files were created.", "run": results["run"]}
    if progress:
        progress("Preparing the indicator file…")
    exported = await save_indicator_export(results, reader)
    if progress and exported.get("status") != "created":
        progress("File creation failed or is unconfirmed; no attachment is claimed.")
    # Only compact status is returned to chat; the JSON file is the deliverable.
    output = {"run": results["run"], "indicator_export": exported}
    if downstream is not None:
        if results["run"]["accepted_findings"] > 0 and exported.get("status") == "created":
            if progress:
                progress("Indicator file confirmed; invoking Historical Enrichment…")
            try:
                output["downstream"] = await downstream(exported, correlation=correlation)
            except Exception:
                output["downstream"] = {"platform_status": "unknown", "application_status": "unknown",
                                        "exports": [], "error": "downstream_failed_or_uncertain"}
        else:
            output["downstream"] = {"platform_status": "not_invoked", "application_status": "unknown",
                                    "exports": [], "error": "no_accepted_findings_or_confirmed_export"}
    if recommendation is not None and output.get("downstream"):
        if progress:
            progress("Checking Enrichment JSON; preparing Recommendation. AWS history remains unavailable.")
            progress("Recommendation may take several minutes. Do not resubmit while this run is in progress.")
        output["recommendation"] = await recommendation(output["downstream"], reader, correlation=correlation)
        if progress:
            progress("Recommendation stage finished or stopped; only verified files will be attached.")
    return output


def status_message(output):
    """Code-generated status only; never include raw uploaded or model strings."""
    if "error" in output:
        return output["error"] + ": " + output["message"]
    run, export = output["run"], output["indicator_export"]
    counts = (f"{run['accepted_findings']} accepted findings; {run['incident_groups']} groups; "
              f"{run['completed']} context analyses completed; {run['failed']} failed; "
              f"{len(run['errors'])} input errors. Run: {run['status']}.")
    if run.get("model") == "none:deterministic-extraction":
        counts = (f"{run['accepted_findings']} accepted findings; {run['incident_groups']} groups. "
                  "Deterministic extraction only; narrative deferred to Recommendation, no Triage model calls. "
                  f"{len(run['errors'])} input errors. Context unavailable by policy; run: {run['status']}.")
    if export.get("status") == "created":
        text = "Created extracted_indicators.json (" + export.get("schema", "alert-indicators/3") + "). " + counts
        child = output.get("downstream")
        if child:
            text += (f" Enrichment platform: {child['platform_status']}; application: {child['application_status']}; "
                     f"{len(child.get('exports', []))}/2 output files confirmed.")
            if child.get("history_status") == "not_configured":
                text += " AWS history: not_configured; no historical searches ran."
            if child.get("error"):
                text += " Downstream unavailable, rejected or unconfirmed; triage export preserved. No automatic retry."
        rec = output.get("recommendation")
        if rec:
            text += (f" Recommendation platform: {rec['platform_status']}; application: {rec['application_status']}; "
                     f"{len(rec.get('exports', []))}/2 output files confirmed.")
            counts = rec.get("counts", {})
            if counts:
                text += f" {counts['completed']}/{counts['incident_count']} incident recommendations completed; {counts['failed']} failed."
            if any(e.get("filename") == "recommendation_report.md" for e in rec.get("exports", [])):
                text += " Open recommendation_report.md for the analyst report. Supporting JSON retains provenance."
            if rec.get("error"):
                text += " Recommendation unavailable or uncertain; earlier outputs preserved. No automatic retry; a timed-out child may still be running."
            text += " Human review required. No actions executed."
        return text
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
        if __package__:
            from .handoff import invoke_enrichment
            from .demo import recommend_from_enrichment
        else:
            from handoff import invoke_enrichment
            from demo import recommend_from_enrichment
        state = runtime.state if runtime is not None else {}
        ids = state.get("source_file_ids", []) if isinstance(state, dict) else getattr(state, "source_file_ids", [])
        progress = TriageProgress(runtime.tool_call_id, SparkEventWriter()) if runtime is not None else None
        cfg = (runtime.config or {}).get("configurable", {}) if runtime is not None else {}
        correlation = {"thread_id": cfg.get("thread_id"), "invocation_id": cfg.get("invocation_id"),
                       "tool_call_id": runtime.tool_call_id if runtime is not None else None}
        output = await analyze_uploaded(ids, SGPResourceClient(), LiveContextClient(), progress=progress,
                                        downstream=invoke_enrichment, correlation=correlation,
                                        recommendation=recommend_from_enrichment)
        if progress and "error" in output:
            progress("Input unavailable or unsupported; no analysis performed.")
        return json.dumps(output, allow_nan=False), {"indicator_export": output.get("indicator_export", {}),
            "enrichment_exports": output.get("downstream", {}).get("exports", []),
            "recommendation_exports": output.get("recommendation", {}).get("exports", []),
            "triage_progress": progress.artifact() if progress else {"text": ""}}
    return StructuredTool.from_function(coroutine=run_triage, name="run_triage",
        description=run_triage.__doc__, response_format="content_and_artifact")
