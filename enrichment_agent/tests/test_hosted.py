"""Managed-file receiver tests, independent of live AWS/SGP."""
import asyncio
import copy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ams.hosted import INPUT_LIMIT, process_uploaded, status_message
from prepare_pod import prepare


class FakeStore:
    def __init__(self, raw, fail_write=None):
        self.raw, self.fail_write = raw, fail_write
        self.reads, self.writes = [], []

    async def read_file_bytes(self, file_id, max_bytes):
        self.reads.append((file_id, max_bytes))
        return SimpleNamespace(status=200, body=self.raw)

    async def write_file(self, filename, content, mime_type):
        self.writes.append((filename, content, mime_type))
        if len(self.writes) == self.fail_write:
            raise RuntimeError("secret: must never escape")
        return SimpleNamespace(status=201, body={"id": "created-" + str(len(self.writes))})


class HostedTests(unittest.TestCase):
    def setUp(self):
        self.raw = (ROOT / "fixtures/triage_v3.json").read_bytes()

    def test_staged_core_is_fresh(self):
        prepare(check=True)

    def test_exact_file_receipt_exports_and_unknown_history(self):
        store = FakeStore(self.raw)
        output = asyncio.run(process_uploaded(["specific-file"], store))
        self.assertEqual(store.reads, [("specific-file", INPUT_LIMIT)])
        self.assertEqual(output["export_status"], "completed")
        self.assertEqual(output["history_status"], "not_configured")
        self.assertEqual(output["run"]["status"], "partial")
        result = json.loads(store.writes[0][1])
        self.assertEqual(result["input"], json.loads(self.raw))
        self.assertEqual(result["handoff_receipt"]["file_id"], "specific-file")
        self.assertTrue(all(r["status"] == "not_configured" for r in result["results"]))
        self.assertIn("no historical searches ran", status_message(output))

    def test_missing_multiple_and_malformed_no_fallback(self):
        for ids in ([], ["a", "b"], [""]):
            store = FakeStore(self.raw)
            self.assertIn("error", asyncio.run(process_uploaded(ids, store)))
            self.assertEqual(store.reads, [])
        for raw in (b'{"schema":"alert-indicators/4"}', b'{"a":1,"a":2}', b"invalid", b" " * (INPUT_LIMIT + 1)):
            store = FakeStore(raw)
            self.assertEqual(asyncio.run(process_uploaded(["x"], store))["error"], "invalid_handoff")
            self.assertEqual(store.writes, [])

    def test_access_failure_and_provider_error_do_not_leak(self):
        class Denied(FakeStore):
            async def read_file_bytes(self, *args, **kwargs):
                return SimpleNamespace(status=403, body=b"secret provider output")
        output = asyncio.run(process_uploaded(["x"], Denied(self.raw)))
        self.assertEqual(output["error"], "file_read_failed")
        self.assertNotIn("secret", json.dumps(output))

    def test_uncertain_writes_stop_without_retry(self):
        for fail_at in (1, 2):
            store = FakeStore(self.raw, fail_write=fail_at)
            output = asyncio.run(process_uploaded(["x"], store))
            self.assertEqual(output["export_status"], "partial")
            self.assertEqual(len(store.writes), fail_at)
            self.assertNotIn("secret", json.dumps(output))
            self.assertEqual(sum(x["status"] == "created" for x in output["exports"]), fail_at - 1)


class SDKContractTests(unittest.TestCase):
    def setUp(self):
        try:
            from ams.input_contract import EnrichmentInput, EnrichmentOutput
            from ams.routing import next_message
        except ImportError:
            self.skipTest("Agent Kit SDK is not installed in this CLI environment")
        self.input, self.output, self.next_message = EnrichmentInput, EnrichmentOutput, next_message

    def test_strict_file_contract_and_reset(self):
        from pydantic import ValidationError
        value = {"task": {"intent": "dispatch", "payload": {"parts": [
            {"type": "resource", "slot": "sources", "resource": {"type": "file", "id": "explicit-id"}}
        ]}}}
        self.assertEqual(self.input.model_validate(value).prepare_state_update()["source_file_ids"], ["explicit-id"])
        empty = {"task": {"intent": "dispatch", "payload": {"parts": [{"type": "text", "text": "next"}]}}}
        self.assertEqual(self.input.model_validate(empty).prepare_state_update()["source_file_ids"], [])
        for bad in ({"messages": []}, {**value, "unexpected": True},
                    {"task": {"intent": "delegate", "payload": {"parts": []}}}):
            with self.assertRaises(ValidationError):
                self.input.model_validate(bad)
        self.assertEqual(set(self.output.model_fields), {"messages", "render_events"})

    def test_one_tool_per_turn_and_no_stale_results(self):
        from langchain_core.messages import HumanMessage, ToolMessage
        first = self.next_message([HumanMessage(content="run")])
        self.assertEqual(first.tool_calls[0]["name"], "run_enrichment")
        message = ToolMessage(name="run_enrichment", tool_call_id="id",
            content=json.dumps({"error": "missing_handoff", "message": "Supply one file."}))
        self.assertFalse(self.next_message([HumanMessage(content="run"), message]).tool_calls)
        self.assertTrue(self.next_message([HumanMessage(content="old"), message, HumanMessage(content="new")]).tool_calls)
