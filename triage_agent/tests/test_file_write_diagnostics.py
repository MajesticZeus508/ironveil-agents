"""All three pod-owned write adapters: safe diagnostics, real SDK, no network."""
import asyncio
import importlib.util
import json
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from triage_agent.plugins.alert_triage import file_writes as triage
from enrichment_agent.ams import file_writes as enrichment
from recommendation_agent.ams import file_writes as reporting

ADAPTERS = (triage, enrichment, reporting)


class WriteTests(unittest.IsolatedAsyncioTestCase):
    def test_agent_owned_copies_match(self):
        self.assertEqual(len({Path(m.__file__).read_bytes() for m in ADAPTERS}), 1)

    async def test_http_failures_and_malformed_successes_never_claim_files(self):
        cases = [(401, {}, "authentication_rejected"), (403, {}, "permission_denied"),
                 (429, {}, "rate_limited"), (503, {}, "storage_unavailable"),
                 (400, {}, "http_rejected"), (302, {}, "http_rejected"),
                 (201, {}, "invalid_success_response"), (201, {"id": ""}, "invalid_success_response"),
                 (201, {"id": "bad\nfile"}, "invalid_success_response"),
                 (True, {"id": "fake"}, "invalid_write_response")]
        for module in ADAPTERS:
            for status, body, category in cases:
                with self.subTest(module=module.__name__, status=status, category=category):
                    calls = []
                    async def write(*args, **kwargs):
                        calls.append(1)
                        return SimpleNamespace(status=status, body={**body, "secret": "PRIVATE"},
                            error="PRIVATE", headers={"Authorization": "PRIVATE"})
                    file_id, failure = await module.write_once(SimpleNamespace(write_file=write), "fixed.json", "{}", "application/json")
                    self.assertIsNone(file_id)
                    self.assertEqual(failure["category"], category)
                    self.assertEqual(calls, [1])
                    self.assertNotIn("PRIVATE", json.dumps(failure))

    async def test_exceptions_are_allowlisted_and_unknown_sent_is_not_false(self):
        SecretError = type("PRIVATE_TOKEN", (Exception,), {})
        for module in ADAPTERS:
            for error, expected in ((TimeoutError("PRIVATE"), "TimeoutError"),
                                    (ValueError("PRIVATE"), "ValueError"),
                                    (SecretError("PRIVATE"), "OtherError")):
                async def write(*args, **kwargs): raise error
                _, failure = await module.write_once(SimpleNamespace(write_file=write), "f", "x", "text/plain")
                self.assertEqual(failure["exception_type"], expected)
                self.assertIsNone(failure["request_may_have_been_sent"])
                self.assertNotIn("PRIVATE", json.dumps(failure))

    async def test_real_sdk_missing_and_invalid_configuration_no_write(self):
        try:
            from spark_agent_kit import SGPResourceClient
        except ImportError:
            self.skipTest("SDK absent")
        for module in ADAPTERS:
            for value, category in (("", "missing_sgp_configuration"), ("PRIVATE_INVALID", "invalid_sgp_configuration")):
                with patch.dict(os.environ, {"SGP_API_URL": value, "SGP_API_EXTRA_HEADERS": ""}):
                    store = SGPResourceClient()
                    with patch.object(store, "write_file", side_effect=AssertionError("must not dispatch")) as write:
                        _, failure = await module.write_once(store, "f", "x", "text/plain")
                    self.assertEqual(write.call_count, 0)
                    self.assertEqual(failure["category"], category)
                    self.assertFalse(failure["request_may_have_been_sent"])
                    self.assertEqual(failure["exception_type"], "ValueError")
                    self.assertNotIn("PRIVATE", json.dumps(failure))

    async def test_real_sdk_failure_envelopes_dispatch_flags_and_success(self):
        try:
            from spark_agent_kit.middleware.resources.results import ResourceFailure, ResourceOk
        except ImportError:
            self.skipTest("SDK absent")
        for module in ADAPTERS:
            for response, category, sent in (
                (ResourceFailure(status=None, error="PRIVATE", cause=TimeoutError("PRIVATE")), "transport_or_client_failure", True),
                (ResourceFailure(status=None, error="PRIVATE", cause=TypeError("PRIVATE"), request_may_have_been_sent=False), "request_not_sent", False),
                (ResourceFailure(status=403, error={"id": "do-not-trust", "secret": "PRIVATE"}), "permission_denied", True),
                (ResourceOk(status=201, body={"id": "valid-id"}), None, None)):
                async def write(*args, **kwargs): return response
                file_id, failure = await module.write_once(SimpleNamespace(write_file=write), "f", "x", "text/plain")
                if category is None:
                    self.assertEqual((file_id, failure), ("valid-id", None))
                else:
                    self.assertIsNone(file_id)
                    self.assertEqual(failure["category"], category)
                    self.assertIs(failure["request_may_have_been_sent"], sent)
                    self.assertNotIn("PRIVATE", json.dumps(failure))

    async def test_cancellation_propagates(self):
        for module in ADAPTERS:
            async def write(*args, **kwargs): raise asyncio.CancelledError()
            with self.assertRaises(asyncio.CancelledError):
                await module.write_once(SimpleNamespace(write_file=write), "f", "x", "text/plain")

    async def test_all_actual_export_paths_expose_diagnostics_and_stop_after_failure(self):
        from triage_agent.plugins.alert_triage.export import save_indicator_export
        from enrichment_agent.ams.hosted import process_input as enrich
        from recommendation_agent.ams.hosted import process_input as recommend
        from enrichment_agent.enrich import enrich as build_enrichment
        from enrichment_agent.history import UnconfiguredAWSHistory
        data = json.loads((ROOT / "enrichment_agent/fixtures/triage_v3.json").read_bytes())
        class BrokenModel:
            model_name = generation_method = "test_stub"
            async def analyze(self, packet): raise RuntimeError("PRIVATE")
        for fail_at in (1, 2):
            for mode in ("triage", "enrichment", "reporting"):
                writes = []
                async def write(*args, **kwargs):
                    writes.append(1)
                    if len(writes) == fail_at: raise TimeoutError("PRIVATE")
                    return SimpleNamespace(status=201, body={"id": "confirmed"})
                store = SimpleNamespace(write_file=write)
                if mode == "triage":
                    output = await save_indicator_export({}, store, handoff=data)
                    entries = [output]
                elif mode == "enrichment":
                    output = await enrich([], data, store)
                    entries = output["exports"]
                    self.assertEqual(output["export_diagnostics"], [e["write_diagnostic"] for e in entries if "write_diagnostic" in e])
                else:
                    output = await recommend([], build_enrichment(data, UnconfiguredAWSHistory()), store, BrokenModel())
                    entries = output["exports"]
                    self.assertIsNone(output["received_file_id"])
                self.assertEqual(len(writes), min(fail_at, 1 if mode == "triage" else 2))
                if fail_at == 1 or mode != "triage":
                    self.assertEqual(entries[-1]["write_diagnostic"]["exception_type"], "TimeoutError")
                    self.assertNotIn("file_id", entries[-1])
                self.assertNotIn("PRIVATE", json.dumps(output))

    def test_remote_diagnostics_allowlist(self):
        for module in ADAPTERS:
            result = module.sanitize_diagnostic({"category": "PRIVATE", "http_status": True,
                "exception_type": "PRIVATE", "request_may_have_been_sent": "PRIVATE", "secret": "PRIVATE"})
            self.assertNotIn("PRIVATE", json.dumps(result))
            self.assertIsNone(result["http_status"])

    def test_diagnostics_survive_verified_child_projection_without_extra_fields(self):
        from triage_agent.plugins.alert_triage.handoff import verified_result
        from test_handoff import projection
        expected = {"file_id": "current", "sha256": "digest"}
        wire = projection(expected)
        result = json.loads(wire["messages"][0]["content"])
        result["export_diagnostics"] = [{"operation": "managed_file_write", "category": "permission_denied",
            "http_status": 403, "exception_type": None, "request_may_have_been_sent": True,
            "body": "PRIVATE", "headers": "PRIVATE"}]
        wire["messages"][0]["content"] = json.dumps(result)
        verified = verified_result(wire, expected)
        self.assertEqual(verified["export_diagnostics"][0]["category"], "permission_denied")
        self.assertNotIn("PRIVATE", json.dumps(verified))
