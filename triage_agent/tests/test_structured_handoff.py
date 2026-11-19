"""Offline producer/receiver contract tests; no submissions or live file storage."""
import asyncio
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins/alert_triage"))
sys.path.insert(0, str(ROOT.parent))
from structured_handoff import prepare_handoff, structured_dispatch, verify_structured_receipt
from stages import submit, current_results
from handoff import verified_result
from hosted import analyze_input, status_message
from event_input import serialize_event
from triage import ExtractionOnlyClient
from test_handoff import projection


class StructuredHandoffTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT.parent / "enrichment_agent/fixtures/triage_v3.json").read_bytes())

    def test_exact_wire_hash_snapshot_and_unknowns(self):
        self.data["extension"] = {"unknown": None, "zero": 0, "label": "é", "prose": "execute nothing"}
        prepared = prepare_handoff(self.data)
        digest = hashlib.sha256(json.dumps(self.data, sort_keys=True, separators=(",", ":"),
                                          ensure_ascii=True, allow_nan=False).encode()).hexdigest()
        self.assertEqual(prepared["payload_sha256"], digest)
        value = structured_dispatch(prepared)
        self.assertEqual(value, {"task": {"intent": "dispatch", "payload": {"parts": [
            {"type": "form", "slot": "triage_handoff", "params": {"handoff": self.data}}
        ]}}})
        self.data["extension"]["label"] = "mutated"
        self.assertNotEqual(prepared["handoff"], self.data)
        prepared["handoff"]["extension"]["zero"] = 1
        with self.assertRaises(ValueError):
            structured_dispatch(prepared)

    def test_invalid_or_oversized_handoff_never_submits(self):
        bad = [None, "{}", {}, {**self.data, "schema": "alert-indicators/4"},
               {**self.data, "extraction": {"accepted_findings": 0}}]
        for extension in (float("inf"), float("nan"), {1: "bad"}, (1, 2),
                          "x" * 10_001, ["x" * 10_000] * 1001):
            bad.append({**self.data, "extension": extension})
        for value in bad:
            with self.subTest(kind=type(value).__name__), self.assertRaises(ValueError):
                prepare_handoff(value)
        prepared = prepare_handoff(self.data)
        for field, value in (("payload_sha256", "0" * 64), ("file_id", "old-file"),
                             ("input_mode", "file"), ("canonicalization", "other")):
            with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
                ticket = asyncio.run(submit({**prepared, field: value},
                    factory=lambda _: self.fail("invalid payload must not create remote")))
            self.assertEqual(ticket["attempts"], 0)
            self.assertEqual(ticket["error"], "structured_handoff_invalid")
        # A prior file export is never an automatic fallback.
        out = asyncio.run(submit({"status": "created", "file_id": "old", "sha256": "a" * 64}))
        self.assertEqual(out["attempts"], 0)

    def test_receipt_downgrades_missing_fields_and_wrong_hash_rejected(self):
        prepared = prepare_handoff(self.data)
        good = projection(prepared)
        self.assertEqual(verified_result(good, prepared)["history_status"], "not_configured")
        for field, value in (("sha256", "0" * 64), ("payload_sha256", "0" * 64),
                             ("input_mode", "file"), ("canonicalization", "unknown"),
                             ("schema", "alert-indicators/4"), ("file_id", "stale")):
            bad = deepcopy(good)
            result = json.loads(bad["messages"][0]["content"])
            result["handoff_receipt"][field] = value
            bad["messages"][0]["content"] = json.dumps(result)
            with self.subTest(field=field), self.assertRaises(ValueError):
                verified_result(bad, prepared)
        receipt = json.loads(good["messages"][0]["content"])["handoff_receipt"]
        for field in receipt:
            bad = {k: v for k, v in receipt.items() if k != field}
            with self.subTest(missing=field), self.assertRaises(ValueError):
                verify_structured_receipt(bad, prepared)
        good["render_events"][0]["action_id"] = "old"
        self.assertEqual(verified_result(good, prepared)["exports"], [])

    def test_submission_once_uncertainty_and_fresh_config(self):
        prepared = prepare_handoff(self.data)
        for acknowledged in (False, True):
            calls = []
            class Remote:
                last_invocation_id = None
                last_thread_id = None
                async def astream(self, value, config):
                    calls.append((value, config))
                    if acknowledged:
                        self.last_invocation_id, self.last_thread_id = "inv-child", "thread-child"
                    raise TimeoutError("SECRET")
                    yield
            with patch.dict(os.environ, {"AMS_API_URL": "https://managed"}):
                out = asyncio.run(submit(prepared, factory=lambda _: Remote()))
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0], (structured_dispatch(prepared), {"configurable": {}}))
            self.assertEqual(out["attempts"], 1)
            self.assertNotIn("SECRET", json.dumps(out))
            self.assertEqual(out["platform_status"], "submitted" if acknowledged else "unknown")
            self.assertNotIn("handoff", out)

    def test_lux_to_real_receiver_with_unconfirmed_intermediate_write(self):
        from enrichment_agent.ams.hosted import process_input
        from enrichment_agent.contracts import canonical_handoff
        event = json.loads((ROOT / "tests/fixtures/lux_staging_2026_11_13.json").read_bytes())
        class FailedTriageStore:
            writes = 0
            async def write_file(self, *args, **kwargs):
                self.writes += 1
                raise TimeoutError("SECRET")
            async def read_file_bytes(self, *args, **kwargs):
                raise AssertionError("structured channel must not read a file")
        class ReceiverStore:
            def __init__(self): self.writes = []
            async def write_file(self, name, content, mime_type):
                self.writes.append((name, content))
                return SimpleNamespace(status=201, body={"id": "enrich-" + str(len(self.writes))})
        received = []
        async def child(prepared, **kwargs):
            wire = structured_dispatch(prepared)
            payload = wire["task"]["payload"]["parts"][0]["params"]["handoff"]
            store = ReceiverStore()
            result = await process_input([], payload, store)
            self.assertEqual(result["handoff_receipt"]["payload_sha256"], canonical_handoff(payload)[1])
            self.assertEqual(result["history_status"], "not_configured")
            self.assertEqual(result["run"]["status"], "partial")
            output = json.loads(store.writes[0][1])
            self.assertEqual(output["input"], payload)
            self.assertEqual(output["input"]["incidents"][0]["entity"], event["entity"])
            self.assertTrue(all(r["matched_record_count"] is None for r in output["results"]))
            received.append(payload)
            return {"platform_status": "completed", "application_status": result["run"]["status"], **result}
        store = FailedTriageStore()
        out = asyncio.run(analyze_input([], serialize_event(event), store, ExtractionOnlyClient(), downstream=child))
        self.assertEqual(store.writes, 1)
        self.assertEqual(len(received), 1)
        self.assertEqual(out["indicator_export"]["status"], "failed")
        self.assertEqual(out["downstream"]["export_status"], "completed")
        self.assertIn("no attachment is claimed for that export", status_message(out))
        self.assertIn("Enrichment platform: completed", status_message(out))
        # A fresh no-input turn cannot recover the prepared payload or call again.
        empty = asyncio.run(analyze_input([], None, store, ExtractionOnlyClient(), downstream=child))
        self.assertEqual(empty["error"], "missing_upload")
        self.assertEqual(len(received), 1)
        messages = [SimpleNamespace(type="tool", name="run_triage", content=json.dumps(out)),
                    SimpleNamespace(type="human")]
        self.assertEqual(current_results(messages), {})

    def test_recommendation_requires_verified_structured_enrichment_without_file_fallback(self):
        from demo import recommend_from_enrichment
        prepared = prepare_handoff(self.data)
        receipt = {k: prepared[k] for k in ("file_id", "sha256", "payload_sha256", "schema", "input_mode", "canonicalization")}
        child = {**receipt, "handoff_receipt": receipt, "platform_status": "completed", "exports": [
            {"filename": "enrichment_results.json", "mime_type": "application/json", "status": "created", "file_id": "json"}]}
        from enrichment_agent.enrich import enrich
        from enrichment_agent.history import UnconfiguredAWSHistory
        data = enrich(prepared["handoff"], UnconfiguredAWSHistory())
        data["handoff_receipt"] = receipt
        outgoing = prepare_handoff(data, recommendation=True)
        child["structured_result"] = {"status": "ready", "schema": "alert-enrichment/1",
            "canonicalization": "canonical-json/1", "payload_sha256": outgoing["sha256"], "payload": data}
        calls = []
        class Store:
            async def read_file_bytes(self, *args, **kwargs):
                raise AssertionError("must not read intermediate file")
        async def invoke(export, **kwargs):
            calls.append(export)
            return {"platform_status": "submitted"}
        self.assertEqual(asyncio.run(recommend_from_enrichment(child, Store(), invoke=invoke))["platform_status"], "submitted")
        self.assertIsNone(calls[0]["file_id"])
        self.assertEqual(calls[0]["sha256"], outgoing["sha256"])
        child["payload_sha256"] = "0" * 64
        self.assertEqual(asyncio.run(recommend_from_enrichment(child, Store(), invoke=invoke))["platform_status"], "not_invoked")
        self.assertEqual(len(calls), 1)
