import asyncio
from copy import deepcopy
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from ams.core import ValidationError, packets, parse, recommend, render_report, validate, validate_narrative
from ams.hosted import process_uploaded, status_message


def fixture(name="verified_demo"):
    return parse((ROOT.parent / "enrichment_agent" / "outputs" / name / "enrichment_results.json").read_bytes())[0]


class Stub:
    model_name = "test_stub"
    generation_method = "test_stub"

    async def analyze(self, packet):
        return {"summary": "TEST STUB: supplied network observation needs review; intent is unknown.",
                "assessment": "Hypothesis: approved operational traffic; verify with the asset owner.",
                "evidence": [{"claim": "Supplied sent-byte value is zero.", "refs": ["O1"]}],
                "recommendations": [
                    {"action": "Ask the asset owner to verify the observed destination and window.",
                     "rationale": "Business context distinguishes expected activity.",
                     "decision_if": "If unapproved, escalate for endpoint review.", "category": "investigate", "requires_approval": False, "refs": ["O1"]},
                    {"action": "Review endpoint telemetry for the supplied window.",
                     "rationale": "Identify the initiating process and user.",
                     "decision_if": "If a suspicious process is confirmed, escalate under the incident-response playbook.", "category": "investigate", "requires_approval": False, "refs": ["O1"]}],
                "escalation_trigger": "Independent endpoint evidence confirms an unauthorized process.",
                "limitations": ["TEST STUB; not model analysis."], "target_observation_ids": ["observation-demo"]}


class Store:
    def __init__(self, data, fail_write=False):
        self.raw = json.dumps(data).encode()
        self.reads, self.writes = [], []
        self.fail_write = fail_write

    async def read_file_bytes(self, file_id, **kwargs):
        self.reads.append(file_id)
        return SimpleNamespace(status=200, body=self.raw)

    async def write_file(self, filename, content, **kwargs):
        self.writes.append((filename, content))
        if self.fail_write:
            raise RuntimeError("secret-provider-error")
        return SimpleNamespace(status=201, body={"id": "created-" + str(len(self.writes))})


class Tests(unittest.TestCase):
    def test_concurrency_bound_order_and_independent_failure(self):
        data = fixture("uploaded_handoff_compatibility")
        class Controlled:
            model_name = "test_stub"
            generation_method = "test_stub"
            active = 0
            peak = 0
            async def analyze(self, packet):
                self.active += 1
                self.peak = max(self.active, self.peak)
                try:
                    # Yield without sleeping or making provider calls.
                    loop = asyncio.get_running_loop()
                    released = loop.create_future()
                    loop.call_soon(released.set_result, None)
                    await released
                    raise RuntimeError("SECRET")
                finally:
                    self.active -= 1
        for concurrency in (1, 2):
            client = Controlled()
            result = asyncio.run(recommend(data, client, concurrency=concurrency))
            self.assertEqual(client.peak, concurrency)
            self.assertEqual(client.active, 0)
            self.assertEqual(result["run"]["failed"], 7)
            self.assertEqual([r["incident_id"] for r in result["incidents"]], [p["incident"]["id"] for p in packets(data)])
            self.assertNotIn("SECRET", json.dumps(result))

    def test_existing_complete_and_pending_contracts(self):
        for name in ("verified_demo", "aws_pending", "uploaded_handoff_compatibility"):
            data = fixture(name)
            validate(data)
        self.assertEqual(len(packets(fixture("uploaded_handoff_compatibility"))), 7)

    def test_null_zero_provenance_and_no_input_mutation(self):
        data = fixture()
        original = deepcopy(data)
        result = asyncio.run(recommend(data, Stub()))
        self.assertEqual(data, original)
        row = result["incidents"][0]["evidence_catalog"]["O1"]["value"]
        self.assertEqual(row["bytes_sent"], 0)
        self.assertIsNone(row["bytes_received"])
        self.assertEqual(row["refs"], data["input"]["indicators"][0]["refs"])
        self.assertIn("TEST STUB", render_report(result))
        self.assertEqual(result["actions_executed"], [])

    def test_pending_stays_partial_after_successful_narrative(self):
        result = asyncio.run(recommend(fixture("aws_pending"), Stub()))
        self.assertEqual(result["run"]["completed"], 1)
        self.assertEqual(result["run"]["status"], "partial")
        self.assertTrue(all(x["value"]["status"] == "not_configured" for k, x in result["incidents"][0]["evidence_catalog"].items() if k.startswith("H")))

    def test_upstream_context_failure_stays_visible(self):
        data = fixture()
        data["input"]["incidents"][0].update(analysis_status="failed", context_status="unavailable")
        result = asyncio.run(recommend(data, Stub()))
        self.assertEqual(result["run"]["status"], "partial")
        self.assertEqual(result["incidents"][0]["upstream_context_status"], "unavailable")

    def test_invalid_join_counts_types_and_history(self):
        mutations = [lambda d: d.update(schema="alert-enrichment/2"),
            lambda d: d["results"][0].update(incident_id="missing"),
            lambda d: d["results"][0].update(observation_ids=["missing"]),
            lambda d: d["results"][0].update(matched_record_count=True),
            lambda d: d["results"][0].update(status="no_match_in_covered_history", search_complete=False),
            lambda d: d["results"][0]["window"].update(end_exclusive="2027-01-01T00:00:00Z"),
            lambda d: d["input"]["indicators"][0].update(src="not-an-ip"),
            lambda d: d["run"].update(query_count=0)]
        for mutation in mutations:
            data = fixture()
            mutation(data)
            with self.assertRaises(ValidationError):
                validate(data)

    def test_duplicate_keys_nonfinite_and_bounds(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":1e999}', b'not json'):
            with self.assertRaises(ValidationError):
                parse(raw)

    def test_invented_targets_refs_ips_domains_and_containment(self):
        packet = packets(fixture())[0]
        mutations = [lambda n: n.update(target_observation_ids=["invented"]),
            lambda n: n["evidence"][0].update(refs=["H999"]),
            lambda n: n.update(summary="Contact 8.8.8.8 for investigation."),
            lambda n: n.update(summary="Investigate evil.example."),
            lambda n: n["recommendations"][0].update(action="Isolate the host now."),
            lambda n: n["recommendations"][0].update(category="containment", requires_approval=False)]
        for mutation in mutations:
            narrative = asyncio.run(Stub().analyze(packet))
            mutation(narrative)
            with self.assertRaises(ValidationError):
                validate_narrative(narrative, packet)

    def test_ratio_clock_and_product_names_are_not_indicators(self):
        packet = packets(fixture())[0]
        n = asyncio.run(Stub().analyze(packet))
        n["summary"] = "Compare ratio 1:10:1 at 10:32:28; review Node.js activity."
        validate_narrative(n, packet)

    def test_model_failure_sanitized_no_fabricated_narrative(self):
        class Broken(Stub):
            async def analyze(self, packet):
                raise RuntimeError("secret-provider-error")
        result = asyncio.run(recommend(fixture(), Broken()))
        self.assertEqual(result["run"]["failed"], 1)
        self.assertIsNone(result["incidents"][0]["narrative"])
        self.assertNotIn("secret-provider-error", json.dumps(result))

    def test_managed_files_and_no_stale_fallback(self):
        store = Store(fixture())
        result = asyncio.run(process_uploaded(["explicit-id"], store, Stub()))
        self.assertEqual(store.reads, ["explicit-id"])
        self.assertEqual(result["export_status"], "completed")
        self.assertEqual(len(store.writes), 2)
        empty = asyncio.run(process_uploaded([], store, Stub()))
        self.assertEqual(empty["error"], "missing_enrichment")
        self.assertEqual(store.reads, ["explicit-id"])

    def test_invalid_input_no_inference_or_export(self):
        store = Store({"schema": "alert-indicators/3"})
        result = asyncio.run(process_uploaded(["id"], store, Stub()))
        self.assertEqual(result["error"], "invalid_enrichment")
        self.assertFalse(store.writes)

    def test_uncertain_write_no_retry_no_false_attachment(self):
        store = Store(fixture(), fail_write=True)
        result = asyncio.run(process_uploaded(["id"], store, Stub()))
        self.assertEqual(result["export_status"], "partial")
        self.assertEqual(len(store.writes), 1)
        self.assertNotIn("file_id", result["exports"][0])
        self.assertNotIn("secret-provider-error", json.dumps(result))
        self.assertIn("not retried", status_message(result))

    def test_markdown_injection_escaped(self):
        data = fixture()
        data["input"]["incidents"][0]["entity"]["id"] = "<script>[run](https://evil.example)"
        report = render_report(asyncio.run(recommend(data, Stub())))
        self.assertNotIn("<script>", report)
        self.assertNotIn("[run](", report)

    def test_sdk_contract_when_available(self):
        try:
            from ams.input_contract import RecommendationDispatch, RecommendationInput
        except ImportError:
            self.skipTest("Agent Kit unavailable in plain CLI environment")
        task = RecommendationDispatch.model_validate({"intent": "dispatch", "payload": {"parts": [{"type": "text", "text": "Analyze"}]}})
        self.assertEqual(task.prepare_state_update()["source_file_ids"], [])
        with self.assertRaises(ValueError):
            RecommendationInput.model_validate({"messages": []})


if __name__ == "__main__":
    unittest.main()
