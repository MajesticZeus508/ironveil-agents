"""Code-generated execution status, not model reasoning. No upload values emitted."""



class TriageProgress:
    def __init__(self, action_id, writer):
        self.action_id, self.writer = action_id, writer

        self.lines = []
        self.stream_available = True

    def __call__(self, message):
        # Only application-authored messages reach this callback.
        if len(self.lines) >= 210:  # Two updates per group, at most 100 records.
            return
        # Blank lines survive Markdown paragraph folding in the thinking renderer.
        line = f"{message}\n\n"
        self.lines.append(line)
        if not self.stream_available:
            return
        from spark_agent_kit.api_contracts.harness.output.events import DeltaEvent, BlockUpdateDeltaPayload, DeltaBlock
        try:
            ordinal, _ = self.writer.allocate_scoped_ordinals(len(self.lines) - 1,
                f"triage-progress:{self.action_id}")
            self.writer.stream_only(DeltaEvent(event_id=ordinal, action_id=self.action_id,
                payload=BlockUpdateDeltaPayload(blocks=(DeltaBlock(type="thinking",
                    block_id=f"triage-progress:{self.action_id}", text=line),))))
        except RuntimeError:
            # Invoke-only clients may lack a custom stream. Preserve final log.
            self.stream_available = False

    def artifact(self):
        return {"text": "".join(self.lines)}
