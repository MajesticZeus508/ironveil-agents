"""One-shot managed-identity AMS handoff; no additive-operation retries."""
import asyncio
import json
import os

# This working source targets Dev; retained staging deployments are unchanged.
ENRICHMENT_AGENT_ID = "420e63bd-8220-48bd-bada-743f0daea46c"
DOWNSTREAM_TIMEOUT = 120


def dispatch_input(file_id):
    return {"task": {"intent": "dispatch", "payload": {"parts": [
        {"type": "text", "text": "Enrich the supplied triage handoff."},
        {"type": "resource", "slot": "sources", "resource": {"type": "file", "id": file_id}},
    ]}}}


def verified_result(values, export, *, recommendation=False):
    """Consume code-owned tool output, never final AI prose or request resources."""
    messages = values.get("messages", [])
    tools = [m for m in messages if isinstance(m, dict) and m.get("type") == "tool"
             and m.get("name") == ("run_recommendation" if recommendation else "run_enrichment")]
    if len(tools) != 1:
        raise ValueError("ambiguous_receiver_result")
    result = json.loads(tools[0]["content"])
    if "error" in result:
        return {"application_status": "failed", "history_status": "unknown", "exports": [],
                "error": "receiver_rejected_handoff"}
    receipt = ({"file_id": result.get("received_file_id"), "sha256": result.get("source_sha256"),
                "schema": "alert-enrichment/1"} if recommendation else result.get("handoff_receipt", {}))
    if (receipt.get("file_id") != export["file_id"] or receipt.get("sha256") != export["sha256"]
            or receipt.get("schema") != ("alert-enrichment/1" if recommendation else "alert-indicators/3")):
        raise ValueError("receipt_mismatch")
    status = result["run"]["status"]
    if status not in {"completed", "partial", "empty"}:
        raise ValueError("invalid_application_status")
    # Only outcome content, not dispatch inputs, can attest created attachments.
    blocks = []
    for event in values.get("render_events", []):
        if (isinstance(event, dict) and event.get("type") == "OutcomeEvent"
                and event.get("action_id") == tools[0].get("tool_call_id") and not event.get("error")):
            blocks.extend((event.get("payload") or {}).get("blocks", []))
    confirmed = {b.get("file_id") for b in blocks if isinstance(b, dict) and b.get("type") == "file"}
    exports = []
    prefix = "recommendation" if recommendation else "enrichment"
    allowed = {f"{prefix}_results.json": "application/json", f"{prefix}_report.md": "text/markdown"}
    for item in result.get("exports", []):
        if (item.get("status") == "created" and item.get("filename") in allowed
                and item.get("mime_type") == allowed[item["filename"]]
                and isinstance(item.get("file_id"), str) and item["file_id"] in confirmed):
            exports.append({k: item[k] for k in ("status", "filename", "mime_type", "file_id")})
    run = result["run"]
    counts = {}
    if recommendation:
        for key in ("incident_count", "completed", "failed"):
            if type(run.get(key)) is not int or not 0 <= run[key] <= 100:
                raise ValueError("invalid_recommendation_counts")
            counts[key] = run[key]
        if counts["completed"] + counts["failed"] != counts["incident_count"]:
            raise ValueError("invalid_recommendation_counts")
    return {"application_status": status, "counts": counts,
            "history_status": "not_configured" if result.get("history_status") == "not_configured" else "unknown",
            "handoff_receipt": receipt, "export_status": result.get("export_status", "unknown"),
            "exports": exports}


def remote_client(base_url, agent_id=ENRICHMENT_AGENT_ID, poll_timeout=90):
    from pydantic import Field
    from spark_agent_kit.agents.remote.ams import AMSRemoteAgent
    from spark_agent_kit.state import AgentState
    # Coercion keeps only explicitly supplied channels; receiver validates its
    # strict Harness task. This client does not prepare or rewrite the task.
    class DispatchState(AgentState):
        task: dict = Field(default_factory=dict)
    return AMSRemoteAgent(agent_id=agent_id, base_url=base_url,
                          state_schema=DispatchState, serialize_json=True,
                          version_type="published", timeout=30, poll_timeout=poll_timeout, poll_interval=2)


async def platform_status(base_url, invocation_id):
    import httpx
    async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
        response = await client.get(f"{base_url.rstrip('/')}/v1/invocations/{invocation_id}")
        response.raise_for_status()
        status = response.json().get("status")
        return status if status in {"queued", "scheduled", "deploying_sandbox", "waiting_for_pod_healthy",
                                    "running", "completed", "failed", "canceled", "interrupted", "requires_action"} else "unknown"


async def invoke_enrichment(export, *, correlation=None, factory=None, status_reader=None, timeout=None,
                            recommendation=False):
    agent_id = "934ba6f7-3dcc-4dfb-9454-acdc92f7a10f" if recommendation else ENRICHMENT_AGENT_ID
    result = {"agent_id": agent_id, "platform_status": "not_invoked",
              "application_status": "unknown", "history_status": "unknown", "exports": [],
              "parent": correlation or {}, "thread_id": None, "invocation_id": None,
              "file_id": export.get("file_id"), "sha256": export.get("sha256"), "attempts": 0}
    if not (export.get("status") == "created" and export.get("file_id") and export.get("sha256")):
        result["error"] = "export_not_confirmed"
        return result
    base = os.getenv("AMS_API_URL") or os.getenv("MCPX_CHECKPOINT_URL")
    if not base:
        result["error"] = "managed_ams_route_unavailable"
        return result
    remote = None
    try:
        remote = factory(base) if factory else remote_client(base, agent_id, 720 if recommendation else 90)
        config = {"configurable": {}}  # Never continue the parent's/previous child's thread.
        async def run():
            result["attempts"] = 1
            result["platform_status"] = "unknown"
            try:
                value = dispatch_input(export["file_id"])
                if recommendation:
                    value["task"]["payload"]["parts"][0]["text"] = "Summarize the enriched alerts and recommend analyst actions."
                values = await remote.ainvoke(value, config=config)
            finally:
                result.update(thread_id=remote.last_thread_id, invocation_id=remote.last_invocation_id)
            if result["invocation_id"]:
                result["platform_status"] = await (status_reader or platform_status)(base, result["invocation_id"])
            if result["platform_status"] == "completed":
                result.update(verified_result(values, export, recommendation=recommendation))
            else:
                result["error"] = "downstream_not_completed"
        await asyncio.wait_for(run(), timeout=(780 if recommendation else DOWNSTREAM_TIMEOUT) if timeout is None else timeout)
    except (TimeoutError, asyncio.TimeoutError):
        result["error"] = "downstream_timeout_uncertain"
    except Exception:
        # Provider/API exception bodies may contain sensitive data. Never retain.
        result["error"] = "downstream_failed_or_uncertain"
    if result.get("error") and result["invocation_id"] and result["platform_status"] == "unknown":
        try:
            result["platform_status"] = await asyncio.wait_for(
                (status_reader or platform_status)(base, result["invocation_id"]), timeout=5)
        except Exception:
            pass
    return result
