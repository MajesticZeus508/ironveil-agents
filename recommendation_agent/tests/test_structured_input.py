"""Reporting receiver regressions; stub inference/storage only."""
import asyncio
from copy import deepcopy
import hashlib
import json
import unittest
from unittest.mock import patch

import test_recommendation as existing
from test_recommendation import fixture, Store, Stub
from ams.core import ValidationError
from ams.hosted import process_input, process_uploaded
from ams.structured_input import canonical_payload


class StructuredTests(unittest.TestCase):
    def test_file_form_equivalence_receipt_and_original_values(self):
        data = fixture("aws_pending")
        data["input"]["indicators"][0]["unknown_extension"] = {"null": None, "zero": 0, "label": "é"}
        before = deepcopy(data)
        a, b = Store(data), Store(data)
        oa = asyncio.run(process_uploaded(["specific-file"], a, Stub()))
        ob = asyncio.run(process_input([], data, b, Stub()))
        expected = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"),
                                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()
        self.assertEqual(ob["handoff_receipt"], {"schema": "alert-enrichment/1", "input_mode": "structured",
            "file_id": None, "sha256": expected, "payload_sha256": expected, "canonicalization": "canonical-json/1"})
        self.assertEqual(oa["source_sha256"], hashlib.sha256(a.raw).hexdigest())
        self.assertEqual(oa["handoff_receipt"]["payload_sha256"], expected)
        self.assertEqual(b.reads, [])
        ra, rb = json.loads(a.writes[0][1]), json.loads(b.writes[0][1])
        for result in (ra, rb):
            self.assertEqual(result["schema"], "alert-recommendations/1")
            self.assertEqual(result["run"]["status"], "partial")
            self.assertEqual(result["actions_executed"], [])
            self.assertTrue(result["human_review_required"])
            self.assertEqual(result["incidents"][0]["evidence_catalog"]["O1"]["value"], data["input"]["indicators"][0])
        for key in ("generated_at", "source_sha256"):
            ra.pop(key)
            rb.pop(key)
        for result in (ra, rb):
            for row in result["incidents"]:
                row.pop("analysis_duration_seconds", None)
        self.assertEqual(ra, rb)
        self.assertEqual(a.writes[1][1], b.writes[1][1])
        self.assertEqual(data, before)

    def test_ambiguity_malformed_bounds_no_inference_or_io(self):
        class Forbidden:
            async def analyze(self, packet):
                raise AssertionError("must not infer")
        data = fixture()
        cycle = []
        cycle.append(cycle)
        deep = None
        for _ in range(42): deep = [deep]
        bad = ["{}", [], {}, {**data, "schema": "alert-indicators/3"}]
        for extension in (float("inf"), float("nan"), {1: "bad"}, (1, 2), b"bytes", cycle, deep,
                          "x" * 10001, ["x" * 10000] * 2001, [None] * 2_000_001):
            bad.append({**data, "extension": extension})
        for mutate in (lambda d: d["results"][0].update(incident_id="missing"),
                       lambda d: d["run"].update(query_count=999),
                       lambda d: d["results"][0].update(status="no_match_in_covered_history", search_complete=False),
                       lambda d: d["input"]["indicators"][0].update(src="bad")):
            value = deepcopy(data)
            mutate(value)
            bad.append(value)
        with patch("ams.hosted.recommend", side_effect=AssertionError("must not infer")):
            for index, value in enumerate(bad):
                store = Store(data)
                with self.subTest(index=index):
                    out = asyncio.run(process_input([], value, store, Forbidden()))
                    self.assertEqual(out["error"], "invalid_enrichment")
                    self.assertEqual((store.reads, store.writes), ([], []))
            store = Store(data)
            self.assertEqual(asyncio.run(process_input(["file"], data, store, Forbidden()))["error"], "ambiguous_enrichment")
            self.assertEqual(asyncio.run(process_input([], None, store, Forbidden()))["error"], "missing_enrichment")
            self.assertEqual((store.reads, store.writes), ([], []))

    def test_real_lux_enrichment_unknowns_and_unavailable_history(self):
        data = existing.Tests().lux_enrichment()
        class LuxStub(Stub):
            async def analyze(self, packet):
                result = await super().analyze(packet)
                result["target_observation_ids"] = []
                return result
        store = Store(data)
        out = asyncio.run(process_input([], data, store, LuxStub()))
        self.assertEqual(out["run"]["completed"], 1)
        self.assertEqual(out["run"]["status"], "partial")
        saved = json.loads(store.writes[0][1])
        self.assertIsNone(saved["incidents"][0]["entity"]["id"])
        self.assertEqual(saved["upstream"]["history_source"]["status"], "not_configured")
        self.assertEqual(saved["actions_executed"], [])

    def test_independent_requests_snapshot_and_no_stale_fallback(self):
        async def run():
            a, b = fixture(), fixture("aws_pending")
            sa, sb = Store(a), Store(b)
            oa, ob = await asyncio.gather(process_input([], a, sa, Stub()), process_input([], b, sb, Stub()))
            self.assertNotEqual(oa["source_sha256"], ob["source_sha256"])
            self.assertEqual((sa.reads, sb.reads), ([], []))
            count = len(sa.writes)
            self.assertEqual((await process_input([], None, sa, Stub()))["error"], "missing_enrichment")
            self.assertEqual(len(sa.writes), count)
        asyncio.run(run())
        data = fixture()
        snapshot, digest = canonical_payload(data)
        data["input"]["indicators"][0]["company"] = "changed"
        self.assertNotEqual(snapshot, data)
        self.assertEqual(canonical_payload(dict(reversed(list(snapshot.items()))))[1], digest)

    def test_uncertain_exports_not_retried(self):
        store = Store(fixture(), fail_write=True)
        out = asyncio.run(process_input([], fixture(), store, Stub()))
        self.assertEqual(out["export_status"], "partial")
        self.assertEqual(len(store.writes), 1)
        self.assertNotIn("secret-provider", json.dumps(out))
        self.assertNotIn("file_id", out["exports"][0])

    def test_sdk_envelope_roundtrip_and_state_replacement(self):
        try:
            from ams.input_contract import RecommendationInput, RecommendationOutput
        except ImportError:
            self.skipTest("Agent Kit absent in CLI environment")
        data = fixture()
        form = {"type": "form", "slot": "enrichment_handoff", "params": {"enrichment": data}}
        file = {"type": "resource", "slot": "sources", "resource": {"type": "file", "id": "current"}}
        def envelope(parts):
            return {"task": {"intent": "dispatch", "payload": {"parts": parts}}}
        state = {}
        for part, ids, structured in ((form, [], data), (file, ["current"], None), (form, [], data)):
            parsed = RecommendationInput.model_validate(envelope([part]))
            update = RecommendationInput.model_validate_json(parsed.model_dump_json()).prepare_state_update()
            state.update(update)
            self.assertEqual(state["source_file_ids"], ids)
            self.assertEqual(state["structured_enrichment"], structured)
            self.assertTrue(update["messages"])
        for parts in ([], [form, file], [form, form], [file, file],
                      [{"type": "text", "text": json.dumps(data)}],
                      [{**form, "params": {"enrichment": json.dumps(data)}}],
                      [{**form, "slot": "wrong"}],
                      [{**form, "params": {"enrichment": data, "extra": True}}]):
            with self.assertRaises(ValueError): RecommendationInput.model_validate(envelope(parts))
        with self.assertRaises(ValueError): RecommendationInput.model_validate({"task": None})
        self.assertEqual(set(RecommendationOutput.model_fields), {"messages", "render_events"})
