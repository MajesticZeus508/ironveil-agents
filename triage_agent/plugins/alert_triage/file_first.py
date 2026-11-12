"""Deterministic routing/status through public model-call middleware hooks.

No outer inference: execute the registered tool once for each fresh request,
then return its code-generated status. Harness still owns tool/file events.
"""
import json
from uuid import uuid4

from langchain.agents.middleware.types import AgentMiddleware, ModelResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

if __package__:
    from .hosted import status_message
else:
    from hosted import status_message


def file_first_message(messages):
    if __package__:
        from .stages import current_results
    else:
        from stages import current_results
    stages = current_results(messages)
    order = ("run_triage", "submit_enrichment", "collect_enrichment", "submit_recommendation", "collect_recommendation")
    for name in order:
        if name not in stages:
            if any(value.get("error") for value in stages.values()):
                break
            return AIMessage(content="", tool_calls=[{
                "name": name, "args": {}, "id": "stage_" + uuid4().hex, "type": "tool_call"}])
    if stages:
        triage = stages.get("run_triage", {})
        if "run" in triage:
            text = status_message({**triage, "downstream": stages.get("collect_enrichment"),
                                   "recommendation": stages.get("collect_recommendation")})
        else:
            text = "Input or extraction failed; no analysis is claimed. Attach one original findings JSON/JSONL file."
        failed = next((name for name in order if stages.get(name, {}).get("error")), None)
        if failed:
            text += f" Workflow stopped at {failed}; previously confirmed attachments remain available. No automatic retry. A submitted child may still be running."
        complete = ("collect_recommendation" in stages and not failed
                    and stages["collect_recommendation"].get("platform_status") == "completed"
                    and len(stages["collect_recommendation"].get("exports", [])) == 2)
        text = ("Investigation stages finished; review partial-data and analysis limitations. " if complete
                else "INVESTIGATION INCOMPLETE. ") + text
        return AIMessage(content=text)
    # Legacy helper below retained for historical tests only.
    current = []
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            break
        current.append(message)
    tools = [m for m in current if isinstance(m, ToolMessage) and m.name == "run_triage"]
    if tools:
        latest = tools[0]
        if getattr(latest, "status", None) == "error":
            return AIMessage(content="Processing failed; no successful export is confirmed. No automatic retry was attempted.")
        try:
            text = status_message(json.loads(latest.content))
        except (ValueError, TypeError, KeyError):
            text = "Processing returned an invalid status; no successful export is confirmed. No automatic retry was attempted."
        return AIMessage(content=text)
    return AIMessage(content="", tool_calls=[{
        "name": "run_triage", "args": {}, "id": "file_first_" + uuid4().hex, "type": "tool_call"}])


class FileFirstMiddleware(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        return ModelResponse(result=[file_first_message(request.state["messages"])])

    async def awrap_model_call(self, request, handler):
        return self.wrap_model_call(request, handler)
