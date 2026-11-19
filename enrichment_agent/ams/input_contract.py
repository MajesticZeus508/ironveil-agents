"""Explicit current-request file OR structured form; never parse prose."""
from typing import Any
from langchain_core.messages import AnyMessage, HumanMessage
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from spark_agent_kit.api_contracts.harness.input import (
    AgentDispatchTask, File, FormPart, ResourcePart, Text, build_task_input_schema,
)
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema
from spark_agent_kit.state import ChatAgentState

if __package__:
    from .contracts import canonical_handoff
else:
    from contracts import canonical_handoff


class HandoffParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    handoff: Any

    @field_validator("handoff", mode="before")
    @classmethod
    def validate_handoff_object(cls, value):
        return canonical_handoff(value)[0]


class TriageHandoff(FormPart[HandoffParams]):
    slot = "triage_handoff"


class Sources(ResourcePart[File]):
    slot = "sources"


class EnrichmentDispatch(AgentDispatchTask[Text | Sources | TriageHandoff]):
    @model_validator(mode="after")
    def validate_files(self):
        files = self.payload.parts.filter(Sources)
        forms = self.payload.parts.filter(TriageHandoff)
        if len(files) + len(forms) != 1:
            raise ValueError("Exactly one handoff file or triage_handoff form is required")
        for part in files:
            value = part.resource.id
            if not value.strip() or len(value) > 256 or any(ord(c) < 32 for c in value):
                raise ValueError("Invalid managed file ID")
        return self

    def prepare_state_update(self):
        update = super().prepare_state_update()
        update["source_file_ids"] = [p.resource.id for p in self.payload.parts.filter(Sources)]
        forms = self.payload.parts.filter(TriageHandoff)
        update["structured_handoff"] = forms[0].params.handoff if forms else None
        if not update.get("messages"):
            update["messages"] = [HumanMessage(content="Process the supplied triage handoff.")]
        return update


class EnrichmentInput(build_task_input_schema(EnrichmentDispatch)):
    @model_validator(mode="after")
    def require_dispatch(self):
        # The SDK accepts task=null by default; that would leave durable input intact.
        if self.task is None:
            raise ValueError("A fresh dispatch with exactly one input mode is required")
        return self


class EnrichmentState(ChatAgentState):
    source_file_ids: list[str] = Field(default_factory=list)
    structured_handoff: Any = None


class EnrichmentOutput(HarnessOutputSchema):
    messages: list[AnyMessage] = Field(default_factory=list)
