"""Donovan's closed text-dispatch input and narrow durable chat output."""
from langchain_core.messages import AnyMessage
from pydantic import Field
from spark_agent_kit.api_contracts.harness.input import AgentDispatchTask, Text, File, ResourcePart, build_task_input_schema
from spark_agent_kit.state import ChatAgentState


class Sources(ResourcePart[File]):
    slot = "sources"


class TriageState(ChatAgentState):
    source_file_ids: list[str] = Field(default_factory=list)
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema


class TriageDispatchTask(AgentDispatchTask[Text | Sources]):
    def prepare_state_update(self):
        update = super().prepare_state_update()
        ids = list(dict.fromkeys(p.resource.id for p in self.payload.parts.filter(Sources)))
        update["source_file_ids"] = ids
        if not update.get("messages"):
            from langchain_core.messages import HumanMessage
            update["messages"] = [HumanMessage(content="Analyze the uploaded findings." if ids else "No file attached.")]
        return update


TriageInput = build_task_input_schema(TriageDispatchTask)


class TriageOutput(HarnessOutputSchema):
    messages: list[AnyMessage] = Field(default_factory=list)


def verify_contract():
    """Offline contract regression checks; no inference or platform access."""
    from pydantic import ValidationError
    good = {"task": {"intent": "dispatch", "payload": {"parts": [
        {"type": "text", "text": "first"}, {"type": "text", "text": "second"}
    ]}}}
    parsed = TriageInput.model_validate(good)
    assert parsed.prepare_state_update()["messages"][0].content == "first\nsecond"
    invalid = [
        {}, {"messages": []},
        {"task": {"intent": "unknown", "payload": {"parts": []}}},
        {**good, "unexpected": True},
        {"task": {"intent": "dispatch", "payload": {"parts": [
            {"type": "text", "text": "x", "unexpected": True}
        ]}}},
    ]
    for value in invalid:
        try:
            TriageInput.model_validate(value)
        except ValidationError:
            continue
        raise AssertionError("Input contract accepted undeclared content")
    schema = TriageInput.model_json_schema()
    assert schema["additionalProperties"] is False
    assert "task" in schema["required"]
    assert set(TriageOutput.model_fields) == {"messages", "render_events"}
    uploaded = TriageInput.model_validate({"task": {"intent": "dispatch", "payload": {"parts": [
        {"type": "resource", "slot": "sources", "resource": {"type": "file", "id": "test-file"}}
    ]}}})
    assert uploaded.prepare_state_update()["source_file_ids"] == ["test-file"]
    assert parsed.prepare_state_update()["source_file_ids"] == []


verify_contract()
