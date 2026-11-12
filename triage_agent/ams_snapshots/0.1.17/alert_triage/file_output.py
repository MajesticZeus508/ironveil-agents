"""Expose only successfully stored indicator exports as Donovan file blocks."""
from spark_agent_kit.api_contracts.harness.output.events import FileBlock, ThinkingBlock
from spark_agent_kit.api_contracts.harness.output.extensions import ToolLifecycle, ToolOutputMiddleware


class IndicatorFileLifecycle(ToolLifecycle):
    def project_tool_outcome(self, context):
        if context.tool_name != "run_triage":
            return ()
        log = context.artifact.get("triage_progress", {}).get("text", "")
        blocks = (ThinkingBlock(block_id=f"triage-progress:{context.action_id}", text=log),) if log else ()
        export = context.artifact.get("indicator_export", {})
        if export.get("status") != "created":
            return blocks
        return blocks + (FileBlock(block_id=context.block_id("indicator-export"),
                          file_id=export["file_id"], name=export["filename"], mime="application/json"),)


def indicator_file_output():
    return ToolOutputMiddleware(output_projector=IndicatorFileLifecycle())
