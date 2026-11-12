"""Checkpoint-sized workflow tools. Submissions and waiting are separate steps."""
import asyncio
import json
import logging
import os
import re
import time
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Annotated

if __package__:
    from .handoff import dispatch_input, remote_client, verified_result, ENRICHMENT_AGENT_ID
    from .hosted import analyze_uploaded
    from .agent import LiveContextClient
    from .triage import ExtractionOnlyClient
else:
    from handoff import dispatch_input, remote_client, verified_result, ENRICHMENT_AGENT_ID
    from hosted import analyze_uploaded
    from agent import LiveContextClient
    from triage import ExtractionOnlyClient

LOG = logging.getLogger(__name__)
# Dev receiver; staging's published source retains its original receiver ID.
RECOMMENDATION_ID = "2cf86942-3a14-40e4-95e5-4a90e752b259"


def current_results(messages):
    """Only code-owned tools after the latest human message belong to this turn."""
    results = {}
    for message in reversed(messages):
        kind = getattr(message, "type", None)
        if kind == "human":
            break
        name = getattr(message, "name", None)
        if kind == "tool" and name not in results:
            if getattr(message, "status", None) == "error":
                results[name] = {"error": "stage_tool_failed", "exports": []}
                continue
            try:
                results[name] = json.loads(message.content)
            except (ValueError, TypeError):
                results[name] = {"error": "invalid_stage_result", "exports": []}
    return results


async def submit(export, recommendation=False, factory=None):
    """Submit once via public SDK stream; stop watching after acknowledgement.

    Closing the observation stream does not cancel the server invocation. A
    separate tool waits using read-only APIs, after this ticket is checkpointed.
    """
    base = os.getenv("AMS_API_URL") or os.getenv("MCPX_CHECKPOINT_URL")
    result = {"platform_status": "unknown", "application_status": "unknown", "exports": [],
              "file_id": export["file_id"], "sha256": export["sha256"],
              "agent_id": RECOMMENDATION_ID if recommendation else ENRICHMENT_AGENT_ID,
              "thread_id": None, "invocation_id": None, "attempts": 1}
    if not base:
        return {**result, "attempts": 0, "error": "managed_ams_route_unavailable"}
    remote = factory(base) if factory else remote_client(base, result["agent_id"], 720 if recommendation else 90)
    value = dispatch_input(export["file_id"])
    if recommendation:
        value["task"]["payload"]["parts"][0]["text"] = "Summarize the enriched alerts and recommend analyst actions."
    stream = remote.astream(value, config={"configurable": {}})
    async def observe():
            # The SDK records IDs before observing SSE. The first received event
            # is sufficient; no child output is trusted at the submission stage.
        async for _ in stream:
            if remote.last_invocation_id:
                break
    try:
        await asyncio.wait_for(observe(), timeout=40)
    except Exception:
        result["error"] = "submission_observation_uncertain"
    finally:
        await stream.aclose()
        result.update(thread_id=remote.last_thread_id, invocation_id=remote.last_invocation_id)
    if result["invocation_id"] and result["thread_id"]:
        result.pop("error", None)
        result["platform_status"] = "submitted"
    else:
        result["error"] = "submission_uncertain_do_not_retry"
    return result


def retry_after_seconds(value, now):
    """Parse bounded header input, never echo it. None means absent/invalid."""
    if not isinstance(value, str) or len(value) > 128:
        return None
    value = value.strip()
    if re.fullmatch(r"[0-9]{1,10}", value):
        return float(value)
    try:
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            return None
        return max(0.0, date.astimezone(timezone.utc).timestamp() - now)
    except (ValueError, TypeError, OverflowError):
        return None


async def collect(ticket, recommendation=False, client=None, timeout=None,
                  *, clock=time.monotonic, sleep=asyncio.sleep, wall_clock=time.time):
    """Read only the checkpointed invocation. Never invoke or continue a thread."""
    import httpx
    result = {**ticket, "exports": [], "application_status": "unknown"}
    started = clock()
    diagnostics = {"get_attempts": 0, "retry_attempts": 0, "error_categories": [],
                   "elapsed_seconds": 0.0, "stop_category": "returned"}
    result["polling_diagnostics"] = diagnostics
    def finish(category="returned"):
        diagnostics.update(stop_category=category, elapsed_seconds=round(clock() - started, 3))
        LOG.info("collection_end category=%s get_attempts=%d retry_attempts=%d elapsed=%.3f",
                 category, diagnostics["get_attempts"], diagnostics["retry_attempts"], clock() - started)
        return result
    if not ticket.get("invocation_id"):
        result["error"] = "missing_child_ticket_do_not_retry"
        return finish("invalid_ticket")
    if (any(not isinstance(ticket.get(key), str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", ticket[key])
            for key in ("invocation_id", "thread_id", "file_id"))
            or not isinstance(ticket.get("sha256"), str)
            or not re.fullmatch(r"[0-9a-f]{64}", ticket["sha256"])):
        result["error"] = "invalid_child_ticket_do_not_retry"
        return finish("invalid_ticket")
    base = os.getenv("AMS_API_URL") or os.getenv("MCPX_CHECKPOINT_URL")
    limit = timeout if timeout is not None else (720 if recommendation else 90)
    deadline = started + limit
    if not base:
        result["error"] = "managed_ams_route_unavailable"
        return finish("route_unavailable")
    async def pause(delay):
        remaining = deadline - clock()
        if remaining <= 0 or delay >= remaining:
            raise TimeoutError
        await sleep(delay)

    async def get(http, path):
        # This is the sole retry seam: exact invocation GETs, never SDK submit,
        # thread creation, file reads/writes, JSON parsing or receipt validation.
        while True:
            remaining = deadline - clock()
            if remaining <= 0:
                raise TimeoutError
            bound = min(30.0, remaining)
            diagnostics["get_attempts"] += 1
            retry_after = None
            try:
                response = await asyncio.wait_for(http.get(path, timeout=bound), timeout=bound)
                if clock() >= deadline:
                    raise TimeoutError
                response.raise_for_status()
                return response
            except (httpx.ConnectTimeout, httpx.ReadTimeout) as exc:
                category = "connect_timeout" if isinstance(exc, httpx.ConnectTimeout) else "read_timeout"
            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code
                category = ("authentication" if status == 401 else "authorization" if status == 403
                            else "rate_limited" if status == 429 else "transient_http"
                            if status in {500, 502, 503, 504} else "permanent_http")
                if status not in {429, 500, 502, 503, 504}:
                    diagnostics["error_categories"].append(category)
                    diagnostics["stop_category"] = category
                    raise
                retry_after = retry_after_seconds(exc.response.headers.get("Retry-After"), wall_clock())
            except TimeoutError:
                # Hard per-request wall-clock bound, scoped only to this GET.
                category = "request_timeout"
            diagnostics["error_categories"].append(category)
            if diagnostics["retry_attempts"] >= 3:
                diagnostics["stop_category"] = "retry_exhausted"
                raise RuntimeError from None
            delay = max(2 ** diagnostics["retry_attempts"], retry_after or 0)
            if delay > 10:
                diagnostics["stop_category"] = "retry_after_exceeds_bound"
                raise RuntimeError from None
            await pause(delay)
            diagnostics["retry_attempts"] += 1

    async def read(http):
            while True:
                response = await get(http, f"{base.rstrip('/')}/v1/invocations/{ticket['invocation_id']}")
                data = response.json()
                status = data.get("status")
                if status not in {"queued", "scheduled", "deploying_sandbox", "waiting_for_pod_healthy",
                                  "running", "completed", "failed", "canceled", "interrupted", "requires_action"}:
                    raise ValueError
                result["platform_status"] = status
                if status == "completed":
                    output = await get(http, f"{base.rstrip('/')}/v1/invocations/{ticket['invocation_id']}/output")
                    if output.status_code == 204:
                        await pause(2)
                        continue
                    result.pop("error", None)
                    result.update(verified_result(output.json(), ticket, recommendation=recommendation))
                    return
                if status not in {"queued", "scheduled", "deploying_sandbox", "waiting_for_pod_healthy", "running"}:
                    result["error"] = "child_not_completed"
                    # Fixed platform code only; never persist free-form diagnostic text.
                    code = data.get("failure_code")
                    if code in {"GRAPH_EXECUTION_ERROR", "GRAPH_INPUT_INVALID"}:
                        result["failure_code"] = code
                    return
                await pause(2)
    try:
        if client is not None:
            await asyncio.wait_for(read(client), timeout=limit)
        else:
            async with httpx.AsyncClient(timeout=30, follow_redirects=False) as http:
                await asyncio.wait_for(read(http), timeout=limit)
    except Exception as exc:
        result["error"] = "collection_timeout_uncertain" if isinstance(exc, TimeoutError) else "collection_failed_uncertain"
        category = diagnostics["stop_category"]
        if isinstance(exc, TimeoutError):
            category = "deadline_exceeded"
        elif category == "returned":
            category = "invalid_data_or_integrity" if isinstance(exc, (ValueError, KeyError, TypeError, AttributeError)) else "permanent_read_failure"
        return finish(category)
    return finish("child_not_completed" if result.get("error") == "child_not_completed" else "returned")


def stage_artifact(name, result):
    exports = ([result["indicator_export"]] if name == "run_triage" and result.get("indicator_export")
               else result.get("exports", []))
    return {"stage_exports": exports}


def make_stage_tools(workdir):
    from langchain.tools import ToolRuntime
    from langchain_core.tools import InjectedToolArg, StructuredTool
    from spark_agent_kit import SGPResourceClient
    if __package__:
        from . import demo
    else:
        import demo

    def state(runtime):
        return runtime.state if isinstance(runtime.state, dict) else runtime.state.model_dump()

    async def execute(name, runtime):
        started = time.monotonic()
        LOG.info("workflow_stage_start stage=%s", name)
        try:
            values = state(runtime)
            prior = current_results(values.get("messages", []))
            store = SGPResourceClient()
            if name == "run_triage":
                client = ExtractionOnlyClient() if os.getenv("TRIAGE_EXTRACTION_ONLY", "true").lower() == "true" else LiveContextClient()
                result = await analyze_uploaded(values.get("source_file_ids", []), store, client)
            elif name == "submit_enrichment":
                export = prior.get("run_triage", {}).get("indicator_export", {})
                result = await submit(export) if export.get("status") == "created" else {"error": "triage_export_unavailable"}
            elif name == "collect_enrichment":
                result = await collect(prior.get("submit_enrichment", {}))
            elif name == "submit_recommendation":
                async def begin(export, **kwargs):
                    return await submit(export, recommendation=True)
                result = await demo.recommend_from_enrichment(prior.get("collect_enrichment", {}), store, invoke=begin)
            else:
                result = await collect(prior.get("submit_recommendation", {}), recommendation=True)
        except asyncio.CancelledError:
            LOG.warning("workflow_stage_interrupted stage=%s elapsed=%.3f", name, time.monotonic() - started)
            raise  # Cancellation must never be converted into a successful checkpoint.
        except Exception as exc:
            result = {"error": "stage_failed_uncertain", "error_class": safe_error_class(exc), "exports": []}
        result["diagnostics"] = {"stage": name, "elapsed_seconds": round(time.monotonic() - started, 3),
                                 "retry_policy": "no_submission_retry"}
        LOG.info("workflow_stage_end stage=%s elapsed=%.3f outcome=%s invocation_id=%s", name,
                 time.monotonic() - started, result.get("error", "returned"), result.get("invocation_id"))
        return json.dumps(result, allow_nan=False), stage_artifact(name, result)

    tools = []
    for name in ("run_triage", "submit_enrichment", "collect_enrichment", "submit_recommendation", "collect_recommendation"):
        # A factory gives every callable a fixed name without a model-selectable argument.
        def make(name):
            async def tool(*, runtime: Annotated[ToolRuntime, InjectedToolArg]) -> tuple:
                return await execute(name, runtime)
            return StructuredTool.from_function(coroutine=tool, name=name,
                description=f"Code-routed workflow stage {name}; no user-supplied IDs or paths.",
                response_format="content_and_artifact")
        tools.append(make(name))
    return tools


def safe_error_class(exc):
    name = type(exc).__name__
    return name if name in {"ValueError", "KeyError", "TypeError", "TimeoutError", "ReadTimeout", "HTTPStatusError"} else "StageError"
