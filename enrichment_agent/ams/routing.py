"""Public middleware seam: no inference and exactly one processing tool per turn."""
import json
from uuid import uuid4
from langchain.agents.middleware.types import AgentMiddleware, ModelResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from spark_agent_kit.api_contracts.harness.output.events import FileBlock
from spark_agent_kit.api_contracts.harness.output.extensions import ToolLifecycle, ToolOutputMiddleware

if __package__:
    from .hosted import status_message
else:
    from hosted import status_message


def next_message(messages):
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            break
        if isinstance(message, ToolMessage) and message.name == "run_enrichment":
            if getattr(message, "status", None) == "error":
                return AIMessage(content="Enrichment processing failed; no successful export is confirmed. No automatic retry.")
            try:
                return AIMessage(content=status_message(json.loads(message.content)))
            except (ValueError, TypeError, KeyError):
                return AIMessage(content="Invalid processing status; no successful export is confirmed. No automatic retry.")
    return AIMessage(content="", tool_calls=[{"name": "run_enrichment", "args": {},
        "id": "enrichment_" + uuid4().hex, "type": "tool_call"}])


class FileFirstMiddleware(AgentMiddleware):
    def wrap_model_call(self, request, handler):
        return ModelResponse(result=[next_message(request.state["messages"])])

    async def awrap_model_call(self, request, handler):
        return self.wrap_model_call(request, handler)


class ExportLifecycle(ToolLifecycle):
    def project_tool_outcome(self, context):
        if context.tool_name != "run_enrichment":
            return ()
        return tuple(FileBlock(block_id=context.block_id("export-" + str(i)),
                               file_id=item["file_id"], name=item["filename"], mime=item["mime_type"])
                     for i, item in enumerate(context.artifact.get("exports", []))
                     if item.get("status") == "created")


def export_middleware():
    return ToolOutputMiddleware(output_projector=ExportLifecycle())
