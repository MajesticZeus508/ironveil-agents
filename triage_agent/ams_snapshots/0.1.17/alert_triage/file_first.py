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
    # Only inspect this invocation's messages, not a prior turn's tool output.
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
