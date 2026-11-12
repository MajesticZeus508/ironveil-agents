"""Typed current-request file references; no text IDs or stale attachment fallback."""
from langchain_core.messages import AnyMessage, HumanMessage
from pydantic import Field, model_validator
from spark_agent_kit.api_contracts.harness.input import (
    AgentDispatchTask, File, ResourcePart, Text, build_task_input_schema,
)
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema
from spark_agent_kit.state import ChatAgentState


class Sources(ResourcePart[File]):
    slot = "sources"


class EnrichmentDispatch(AgentDispatchTask[Text | Sources]):
    @model_validator(mode="after")
    def validate_files(self):
        files = self.payload.parts.filter(Sources)
        if len(files) > 1:
            raise ValueError("Exactly one handoff file is supported")
        for part in files:
            value = part.resource.id
            if not value.strip() or len(value) > 256 or any(ord(c) < 32 for c in value):
                raise ValueError("Invalid managed file ID")
        return self

    def prepare_state_update(self):
        update = super().prepare_state_update()
        update["source_file_ids"] = [p.resource.id for p in self.payload.parts.filter(Sources)]
        if not update.get("messages"):
            update["messages"] = [HumanMessage(content="Process the supplied triage handoff.")]
        return update


EnrichmentInput = build_task_input_schema(EnrichmentDispatch)


class EnrichmentState(ChatAgentState):
    source_file_ids: list[str] = Field(default_factory=list)


class EnrichmentOutput(HarnessOutputSchema):
    messages: list[AnyMessage] = Field(default_factory=list)
