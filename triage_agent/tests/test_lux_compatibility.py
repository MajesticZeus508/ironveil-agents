"""Observed producer payload regression; mutated cases are synthetic test variants."""
import asyncio
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "alert_triage"))
from triage import analyze, ExtractionOnlyClient, group_findings, parse_jsonl, summarize
from event_input import serialize_event
from export import build_indicator_export
from hosted import analyze_input, analyze_uploaded
from test_event_ingestion import Store


class LuxCompatibilityTests(unittest.TestCase):
    def test_new_observed_labels_preserve_values_without_identity_or_units(self):
        cases = json.loads((ROOT / "tests/fixtures/lux_2026_11_16_review.json").read_text())["cases"]
        for case in cases:
            event = case["finding"]
            with self.subTest(detector=event["detector"]):
                records, info = parse_jsonl(serialize_event(event))
                self.assertEqual(info["errors"], [])
                self.assertEqual(records[0]["finding"], event)
                result = summarize(records)
                metric = result["detector_metrics"][0]
                for key in ("detector", "measures", "observed", "baseline", "z_score"):
                    self.assertEqual(metric[key], event[key])
                self.assertEqual(result["entity"], event["entity"])
                self.assertFalse(any("entity" in ip["roles"] for ip in result["indicators"]["ips"]))
                issue = next(q for q in result["data_quality_issues"] if q["kind"] == "unknown_measure_semantics")
                self.assertEqual(issue["raw_value"]["detector"], event["detector"])
                content = serialize_event(event)
                event_store, file_store = Store(), Store(content.encode())
                asyncio.run(analyze_input([], content, event_store, ExtractionOnlyClient()))
                asyncio.run(analyze_uploaded(["current"], file_store, ExtractionOnlyClient()))
                self.assertEqual(event_store.writes[0]["incidents"], file_store.writes[0]["incidents"])
                self.assertEqual(event_store.writes[0]["indicators"], file_store.writes[0]["indicators"])
                bad = deepcopy(event)
                bad["measures"] = "distinct active hosts"
                self.assertEqual(parse_jsonl(json.dumps(bad))[0], [])

    def setUp(self):
        self.event = json.loads((ROOT / "tests/fixtures/lux_staging_2026_11_13.json").read_text())

    def test_exact_payload_hash_preservation_and_unknown_flags(self):
        content = serialize_event(self.event)
        self.assertEqual(hashlib.sha256(content.encode()).hexdigest(),
                         "55442620a0c28275a512d0ba4b6cde99cd3b807bd34f8edf060ee5e189086480")
        records, info = parse_jsonl(content)
        self.assertEqual(info["errors"], [])
        self.assertEqual(records[0]["finding"], self.event)
        result = summarize(records)
        self.assertEqual(result["entity"], self.event["entity"])
        self.assertEqual(result["incident_key"], self.event["incident_key"])
        self.assertEqual(result["sample_summary"]["unique_exact_rows"], 7)
        metric = result["detector_metrics"][0]
        for key in ("detector", "measures", "observed", "baseline", "z_score", "normalcy_score"):
            self.assertEqual(metric[key], self.event[key])
        self.assertTrue({"unknown_entity", "unknown_measure_semantics"} <=
                        {q["kind"] for q in result["data_quality_issues"]})
        self.assertFalse(any("entity" in ip["roles"] for ip in result["indicators"]["ips"]))

    def test_no_placeholder_group_merge_and_dedup_conflicts_unchanged(self):
        second = deepcopy(self.event)
        second["finding_id"] = "different-unresolved-finding"
        for row in second["evidence"]:
            row["src"] = "192.168.75.252"
        records, info = parse_jsonl(json.dumps([self.event, self.event, second]))
        self.assertEqual(info["duplicate_lines"], 1)
        self.assertEqual(len(group_findings(records)), 2)
        second["finding_id"] = self.event["finding_id"]
        records, info = parse_jsonl(json.dumps([self.event, second]))
        self.assertEqual(records, [])
        self.assertEqual(info["errors"][0]["kind"], "conflicting_id")

    def test_allowlist_is_exact_and_numeric_evidence_validation_remains(self):
        variants = []
        for key, value in (("detector", "to AMS fanout"), ("detector", "to AMS egress_volume_hourly"),
                           ("measures", None), ("measures", "bytes"), ("source", "unapproved/source"),
                           ("entity", None), ("entity", {"type": "host", "id": None, "site": None}),
                           ("entity", {"type": "unknown", "id": "192.168.75.251", "site": None})):
            bad = deepcopy(self.event)
            bad[key] = value
            variants.append(bad)
        bad = deepcopy(self.event)
        bad["evidence"][0]["bytes_sent"] = -1
        variants.append(bad)
        bad = deepcopy(self.event)
        bad["baseline"]["std_dev"] = "unknown"
        variants.append(bad)
        for bad in variants:
            with self.subTest(bad=bad):
                self.assertEqual(parse_jsonl(json.dumps(bad))[0], [])

    def test_file_event_export_equivalence_and_downstream_contract(self):
        content = serialize_event(self.event)
        event_store, file_store = Store(), Store(content.encode())
        event_out = asyncio.run(analyze_input([], content, event_store, ExtractionOnlyClient()))
        asyncio.run(analyze_uploaded(["current-file"], file_store, ExtractionOnlyClient()))
        exported = event_store.writes[0]
        for key in ("incidents", "indicators", "extraction"):
            self.assertEqual(exported[key], file_store.writes[0][key])
        self.assertEqual(event_out["run"]["event_receipt"]["finding_ids"], [self.event["finding_id"]])
        self.assertEqual(exported["incidents"][0]["entity"], self.event["entity"])
        self.assertEqual(len(exported["indicators"]), 7)
        opaque = next(q for q in exported["incidents"][0]["data_quality_issues"] if q["kind"] == "unknown_measure_semantics")
        self.assertEqual(opaque["raw_value"]["measures"], "unknown")
        spec = importlib.util.spec_from_file_location("lux_receiver_contract", ROOT.parent / "enrichment_agent/contracts.py")
        assert spec is not None and spec.loader is not None
        contract = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(contract)
        contract.validate_handoff(exported)

        # Full real receiver compatibility is covered in Recommendation's suite,
        # using the actual unconfigured-history Enrichment adapter.

    def test_multiple_sources_never_establish_entity_and_legacy_unchanged(self):
        self.event["evidence"][1]["src"] = "192.168.75.252"
        data = asyncio.run(analyze(serialize_event(self.event), ExtractionOnlyClient()))
        self.assertEqual(data["results"][0]["entity"], self.event["entity"])
        self.assertEqual(data["results"][0]["sample_summary"]["distinct_sample_sources"], 2)
        self.assertEqual(build_indicator_export(data)["incidents"][0]["entity"]["id"], None)
        records, info = parse_jsonl((ROOT / "staging_input_verification.json").read_text())
        self.assertEqual(info["accepted_findings"], 17)
        self.assertEqual(len(group_findings(records)), 7)
