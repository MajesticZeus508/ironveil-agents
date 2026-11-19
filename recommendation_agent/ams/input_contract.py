"""Closed Harness dispatch; one current-request file OR enrichment form."""
from typing import Any
from langchain_core.messages import AnyMessage, HumanMessage
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from spark_agent_kit.api_contracts.harness.input import AgentDispatchTask, File, FormPart, ResourcePart, Text, build_task_input_schema
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema
from spark_agent_kit.state import ChatAgentState

if __package__:
    from .structured_input import canonical_payload
else:
    from structured_input import canonical_payload


class EnrichmentParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enrichment: Any

    @field_validator("enrichment", mode="before")
    @classmethod
    def validate_object(cls, value):
        return canonical_payload(value)[0]


class EnrichmentHandoff(FormPart[EnrichmentParams]):
    slot = "enrichment_handoff"


class Sources(ResourcePart[File]):
    slot = "sources"


class RecommendationDispatch(AgentDispatchTask[Text | Sources | EnrichmentHandoff]):
    @model_validator(mode="after")
    def validate_files(self):
        files = self.payload.parts.filter(Sources)
        if len(files) + len(self.payload.parts.filter(EnrichmentHandoff)) != 1:
            raise ValueError("Exactly one enrichment file or enrichment_handoff form is required")
        for part in files:
            value = part.resource.id
            if not value.strip() or len(value) > 256 or any(ord(c) < 32 for c in value):
                raise ValueError("Invalid managed file ID")
        return self

    def prepare_state_update(self):
        update = super().prepare_state_update()
        update["source_file_ids"] = [p.resource.id for p in self.payload.parts.filter(Sources)]
        forms = self.payload.parts.filter(EnrichmentHandoff)
        update["structured_enrichment"] = forms[0].params.enrichment if forms else None
        if not update.get("messages"):
            update["messages"] = [HumanMessage(content="Analyze the supplied enrichment handoff.")]
        return update


class RecommendationInput(build_task_input_schema(RecommendationDispatch)):
    @model_validator(mode="after")
    def require_task(self):
        if self.task is None:
            raise ValueError("A fresh dispatch is required")
        return self


class RecommendationState(ChatAgentState):
    source_file_ids: list[str] = Field(default_factory=list)
    structured_enrichment: Any = None


class RecommendationOutput(HarnessOutputSchema):
    messages: list[AnyMessage] = Field(default_factory=list)
