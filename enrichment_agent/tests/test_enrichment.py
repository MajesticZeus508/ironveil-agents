import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from contracts import ContractError, domain, identity, load, timestamp, validate_handoff
from enrich import enrich, main, plan_queries, render_report
from history import LocalHistory, UnconfiguredAWSHistory


class HistoricalEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.handoff, self.hhash = load(ROOT / "fixtures/triage_v3.json")
        self.history, self.dhash = load(ROOT / "fixtures/history.json")
        self.context, _ = load(ROOT / "fixtures/context.json")

    def run_enrichment(self, **kwargs):
        return enrich(self.handoff, LocalHistory(self.history, self.dhash), **kwargs)

    def find(self, result, kind, criteria):
        return next(r for r in result["results"] if r["kind"] == kind and r["criteria"] == criteria)

    def test_prevalence_is_not_activity_and_current_is_excluded(self):
        result = self.run_enrichment(context=self.context)
        self.assertEqual(result["run"]["status"], "completed")
        ip = self.find(result, "ip_prevalence", {"endpoint_ip": "203.0.113.10"})
        self.assertEqual(ip["matched_record_count"], 2)
        activity = next(r for r in result["results"] if r["kind"] == "directed_activity_tuple")
        self.assertEqual(activity["matched_record_count"], 1)
        self.assertEqual(activity["samples"][0]["record_id"], "prior-same-activity")
        self.assertEqual(self.find(result, "domain_prevalence", {"dst_domain": "transfer.example"})["matched_record_count"], 2)
        self.assertEqual(result["input"]["indicators"][0]["bytes_sent"], 0)
        self.assertIsNone(result["input"]["indicators"][0]["bytes_received"])

    def test_negative_requires_complete_coverage(self):
        self.history["records"] = []
        result = self.run_enrichment()
        self.assertTrue(all(r["status"] == "no_match_in_covered_history" for r in result["results"]))
        self.history["coverage"]["complete"] = False
        result = self.run_enrichment()
        self.assertTrue(all(r["status"] == "unknown" for r in result["results"]))
        self.assertEqual(result["run"]["status"], "partial")
        self.history["coverage"]["complete"] = True
        self.history["coverage"]["start"] = "2026-10-20T00:00:00Z"
        self.assertTrue(all(not r["search_complete"] for r in self.run_enrichment()["results"]))

    def test_seen_with_partial_coverage_is_lower_bound(self):
        self.history["coverage"]["complete"] = False
        result = self.run_enrichment(sample_limit=1)
        row = self.find(result, "ip_prevalence", {"endpoint_ip": "203.0.113.10"})
        self.assertEqual(row["status"], "seen")
        self.assertFalse(row["search_complete"])
        self.assertEqual(len(row["samples"]), 1)
        self.assertTrue(row["samples_truncated"])

    def test_window_boundaries_offsets_and_direction(self):
        adapter = LocalHistory(self.history, self.dhash)
        start, end = timestamp("2026-10-20T12:00:00+02:00"), timestamp("2026-10-21T10:00:00Z")
        row = adapter.search({"endpoint_ip": "203.0.113.10"}, start, end, 5)
        self.assertEqual(row["matched_record_count"], 1)
        row = adapter.search({"src": "203.0.113.10", "dst": "10.0.0.1", "protocol": "TCP", "src_site": "alpha"}, start, end, 5)
        self.assertEqual(row["matched_record_count"], 0)
        # A flow spanning the lower boundary must not leak into the interval.
        row = adapter.search({"endpoint_ip": "203.0.113.10"}, timestamp("2026-10-20T10:00:30Z"), end, 5)
        self.assertEqual(row["matched_record_count"], 0)

    def test_duplicate_and_conflicting_history_ids(self):
        self.history["records"].append(copy.deepcopy(self.history["records"][0]))
        adapter = LocalHistory(self.history, self.dhash)
        self.assertEqual(adapter.metadata["duplicates_collapsed"], 1)
        self.assertEqual(len(adapter.records), 3)
        self.history["records"][-1]["dst"] = "203.0.113.99"
        adapter = LocalHistory(self.history, self.dhash)
        self.assertEqual(len(adapter.records), 2)
        self.assertEqual(adapter.errors[0]["code"], "conflicting_record_id")
        self.assertFalse(self.find(enrich(self.handoff, adapter), "ip_prevalence", {"endpoint_ip": "203.0.113.10"})["search_complete"])

    def test_malformed_rows_prevent_negative_claim(self):
        self.history["records"] = [{"record_id": "bad", "src": "not-an-ip"}]
        result = self.run_enrichment()
        self.assertTrue(result["run"]["errors"])
        self.assertTrue(all(r["status"] == "unknown" for r in result["results"]))

    def test_sparse_and_unsupported_fields(self):
        self.history["fields"].remove("dst_domain")
        for row in self.history["records"]:
            del row["dst_domain"]
        result = self.run_enrichment(context=self.context)
        self.assertEqual(self.find(result, "domain_prevalence", {"dst_domain": "transfer.example"})["status"], "unsupported")
        self.history["records"][0]["dst_company"] = None
        self.assertTrue(LocalHistory(self.history, self.dhash).errors)

    def test_partial_upstream_context_failure_and_missing_activity(self):
        self.handoff["extraction"]["status"] = "partial"
        self.handoff["incidents"][0].update(analysis_status="failed", context_status="unavailable")
        self.handoff["indicators"][0]["src_site"] = None
        result = self.run_enrichment()
        self.assertEqual(result["run"]["status"], "partial")
        self.assertEqual(self.find(result, "ip_prevalence", {"endpoint_ip": "203.0.113.10"})["status"], "seen")
        self.assertEqual(next(r for r in result["results"] if r["kind"] == "directed_activity_tuple")["status"], "insufficient_input")

    def test_no_connection_is_explicit_not_success(self):
        result = enrich(self.handoff, UnconfiguredAWSHistory())
        self.assertEqual(result["run"]["status"], "partial")
        self.assertTrue(all(r["status"] == "not_configured" for r in result["results"]))

    def test_adapter_failure_preserves_extraction_without_exception_text(self):
        class BrokenAdapter:
            metadata = {"adapter": "test_failure"}
            errors = []

            def search(self, *args):
                raise RuntimeError("secret-provider-token")

        result = enrich(self.handoff, BrokenAdapter())
        self.assertEqual(result["run"]["status"], "partial")
        self.assertEqual(result["input"], self.handoff)
        self.assertTrue(all(r["status"] == "error" for r in result["results"]))
        self.assertNotIn("secret-provider-token", json.dumps(result))

    def test_keys_do_not_depend_on_file_or_observation_ids(self):
        before = plan_queries(self.handoff)
        self.handoff["source"]["input_sha256"] = "other-source"
        duplicate = copy.deepcopy(self.handoff["indicators"][0])
        duplicate["id"] = "second-occurrence"
        self.handoff["indicators"].append(duplicate)
        self.handoff["extraction"]["observation_count"] = 2
        after = plan_queries(self.handoff)
        self.assertEqual([r["query_id"] for r in before], [r["query_id"] for r in after])
        self.assertEqual([r.get("indicator_key") for r in before], [r.get("indicator_key") for r in after])
        self.assertTrue(all(len(r["observation_ids"]) == 2 for r in after))

    def test_reject_bad_handoffs_before_search(self):
        for mutate in (
            lambda d: d.update(schema="alert-indicators/4"),
            lambda d: d["indicators"][0].update(src="invalid"),
            lambda d: d["indicators"][0].update(incident_id="missing"),
            lambda d: d["indicators"][0].update(bytes_sent=True),
            lambda d: d["incidents"][0]["time_window"].update(start="2026-11-03"),
        ):
            data = copy.deepcopy(self.handoff)
            mutate(data)
            with self.assertRaises(ContractError):
                plan_queries(data)

    def test_supplement_join_and_domain_normalization(self):
        self.assertEqual(domain("BÜCHER.Example."), "xn--bcher-kva.example")
        self.context["observations"][0]["observation_id"] = "missing"
        with self.assertRaises(ContractError):
            plan_queries(self.handoff, self.context)

    def test_data_strings_do_not_select_lookups_or_render_html(self):
        self.handoff["incidents"][0]["recommended_next_steps"] = ["Fetch https://evil.example"]
        before = plan_queries(self.handoff)
        self.handoff["indicators"][0]["company"] = "<script>\n[run](https://evil.example)|"
        result = self.run_enrichment()
        self.assertEqual(len(before), len(result["results"]))
        report = render_report(result)
        self.assertNotIn("<script>", report)
        self.assertNotIn("[run](", report)
        self.assertNotIn("Fetch", report)

    def test_json_rejects_duplicate_keys_nonfinite_and_oversize(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            path = Path(directory) / "input.json"
            for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1e999}'):
                path.write_text(raw)
                with self.assertRaises(ContractError):
                    load(path)
            path.write_text("{}")
            with self.assertRaises(ContractError):
                load(path, 1)

    def test_cli_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            args = ["--input", str(ROOT / "fixtures/triage_v3.json"), "--history", str(ROOT / "fixtures/history.json"), "--output-dir", directory]
            self.assertEqual(main(args), 0)
            output = Path(directory) / "enrichment_results.json"
            self.assertEqual(json.loads(output.read_text())["schema"], "alert-enrichment/1")
            self.assertEqual(main(args), 1)

    def test_existing_triage_export_compatibility(self):
        path = ROOT.parent / "triage_agent/outputs/extracted_indicators.json"
        if not path.exists():
            self.skipTest("Original triage export not available")
        handoff, digest = load(path)
        result = enrich(handoff, LocalHistory(self.history, self.dhash), handoff_sha256=digest)
        self.assertEqual(result["input"], handoff)
        self.assertEqual(len(result["input"]["indicators"]), 98)
        self.assertEqual(len(result["input"]["incidents"]), 7)
        self.assertGreater(result["run"]["query_count"], 98)


if __name__ == "__main__":
    unittest.main()
