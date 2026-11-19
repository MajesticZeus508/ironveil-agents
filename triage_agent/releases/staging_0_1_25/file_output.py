"""Expose only successfully stored indicator exports as Donovan file blocks."""
from spark_agent_kit.api_contracts.harness.output.events import FileBlock, ThinkingBlock
from spark_agent_kit.api_contracts.harness.output.extensions import ToolLifecycle, ToolOutputMiddleware


class IndicatorFileLifecycle(ToolLifecycle):
    def project_tool_outcome(self, context):
        stage_exports = context.artifact.get("stage_exports")
        if stage_exports is not None:
            return tuple(FileBlock(block_id=context.block_id(f"stage-export-{index}"),
                                   file_id=item["file_id"], name=item["filename"], mime=item["mime_type"])
                         for index, item in enumerate(stage_exports) if item.get("status") == "created")
        if context.tool_name != "run_triage":
            return ()
        log = context.artifact.get("triage_progress", {}).get("text", "")
        blocks = (ThinkingBlock(block_id=f"triage-progress:{context.action_id}", text=log),) if log else ()
        export = context.artifact.get("indicator_export", {})
        if export.get("status") != "created":
            return blocks
        blocks += (FileBlock(block_id=context.block_id("indicator-export"),
                             file_id=export["file_id"], name=export["filename"], mime="application/json"),)
        for index, item in enumerate(context.artifact.get("enrichment_exports", [])):
            if item.get("status") == "created":
                blocks += (FileBlock(block_id=context.block_id(f"enrichment-export-{index}"),
                                     file_id=item["file_id"], name=item["filename"], mime=item["mime_type"]),)
        for index, item in enumerate(context.artifact.get("recommendation_exports", [])):
            if item.get("status") == "created":
                blocks += (FileBlock(block_id=context.block_id(f"recommendation-export-{index}"),
                                     file_id=item["file_id"], name=item["filename"], mime=item["mime_type"]),)
        return blocks


def indicator_file_output():
    return ToolOutputMiddleware(output_projector=IndicatorFileLifecycle())
