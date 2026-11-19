"""Closed Donovan file / structured LUX dispatch input and durable chat output."""
from langchain_core.messages import AnyMessage
from pydantic import BaseModel, ConfigDict, Field, model_validator
from spark_agent_kit.api_contracts.harness.input import AgentDispatchTask, Text, File, FormPart, ResourcePart, build_task_input_schema
from spark_agent_kit.state import ChatAgentState
if __package__:
    from .event_input import serialize_event
else:
    from event_input import serialize_event


class Sources(ResourcePart[File]):
    slot = "sources"


class LuxEventParams(BaseModel):
    model_config = ConfigDict(extra="forbid")
    # The Events Log payload is the finding itself, not a guessed envelope path.
    event: dict

    @model_validator(mode="after")
    def bounded_event(self):
        serialize_event(self.event)
        return self


class LuxEvent(FormPart[LuxEventParams]):
    slot = "lux_event"


class TriageState(ChatAgentState):
    source_file_ids: list[str] = Field(default_factory=list)
    lux_event_json: str | None = None
from spark_agent_kit.api_contracts.harness.output import HarnessOutputSchema


class TriageDispatchTask(AgentDispatchTask[Text | Sources | LuxEvent]):
    @model_validator(mode="after")
    def unambiguous_input(self):
        events = self.payload.parts.filter(LuxEvent)
        if len(events) > 1 or (events and self.payload.parts.filter(Sources)):
            raise ValueError("Supply one LUX event or managed findings file, not both.")
        if events:
            # Bound the whole event dispatch as well as its finding payload.
            serialize_event(self.model_dump(mode="json"))
        return self

    def prepare_state_update(self):
        update = super().prepare_state_update()
        ids = list(dict.fromkeys(p.resource.id for p in self.payload.parts.filter(Sources)))
        update["source_file_ids"] = ids
        event = self.payload.parts.filter(LuxEvent).first()
        # Reset BOTH input channels on every fresh dispatch, including text-only.
        update["lux_event_json"] = serialize_event(event.params.event) if event is not None else None
        if not update.get("messages"):
            from langchain_core.messages import HumanMessage
            update["messages"] = [HumanMessage(content="Analyze the supplied LUX event." if event is not None else
                ("Analyze the uploaded findings." if ids else "No file attached."))]
        return update


class TriageInput(build_task_input_schema(TriageDispatchTask)):
    @model_validator(mode="after")
    def explicit_dispatch(self):
        if self.task is None:
            raise ValueError("An explicit dispatch is required; previous input cannot be reused.")
        return self


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
    assert parsed.prepare_state_update()["lux_event_json"] is None
    event_part = {"type": "form", "slot": "lux_event", "params": {"event": {"schema": "swoop-ueba-finding/1"}}}
    event_input = {"task": {"intent": "dispatch", "payload": {"parts": [event_part]}}}
    event_update = TriageInput.model_validate(event_input).prepare_state_update()
    assert event_update["source_file_ids"] == []
    assert event_update["lux_event_json"] == '{"schema":"swoop-ueba-finding/1"}'
    assert event_update["messages"][0].type == "human"
    for parts in ([event_part, event_part], [event_part, uploaded.task.payload.parts[0].model_dump()]):
        try:
            TriageInput.model_validate({"task": {"intent": "dispatch", "payload": {"parts": parts}}})
        except ValidationError:
            continue
        raise AssertionError("Ambiguous event input accepted")


verify_contract()
