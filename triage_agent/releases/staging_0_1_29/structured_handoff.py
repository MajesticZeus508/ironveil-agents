"""Triage-owned canonical-json/1 transport; no file or prose fallback.

Keep these wire bounds/hash semantics in sync with Enrichment's AMS_HANDOFF.md.
Receiver remains authoritative for full alert-indicators/3 semantic validation.
"""
import hashlib
import json
import math

INPUT_LIMIT = 10_000_000


def prepare_handoff(handoff, *, recommendation=False):
    """Snapshot the code-owned object and describe its canonical payload hash."""
    nodes = 0

    def check(value, depth=0):
        nonlocal nodes
        nodes += 1
        if nodes > (2_000_000 if recommendation else 1_000_000) or depth > 40:
            raise ValueError("handoff_structure_limit")
        kind = type(value)
        if kind is str:
            if len(value) > 10_000:
                raise ValueError("handoff_string_limit")
        elif kind is dict:
            for key, child in value.items():
                if type(key) is not str:
                    raise ValueError("handoff_json_key")
                check(key, depth + 1)
                check(child, depth + 1)
        elif kind is list:
            for child in value:
                check(child, depth + 1)
        elif kind is float:
            if not math.isfinite(value):
                raise ValueError("handoff_nonfinite")
        elif value is not None and kind not in (bool, int):
            raise ValueError("handoff_json_type")

    check(handoff)
    schema = "alert-enrichment/1" if recommendation else "alert-indicators/3"
    if type(handoff) is not dict or handoff.get("schema") != schema:
        raise ValueError("handoff_schema")
    triage = handoff.get("input", {}) if recommendation else handoff
    extraction = triage.get("extraction", {})
    if (type(extraction) is not dict or type(extraction.get("accepted_findings")) is not int
            or extraction["accepted_findings"] <= 0):
        raise ValueError("handoff_no_accepted_findings")
    for key, limit in (("incidents", 1000), ("indicators", 10_000)):
        values = triage.get(key)
        if type(values) is not list or len(values) > (100 if recommendation and key == "incidents" else limit):
            raise ValueError("handoff_inventory_limit")
    chunks, size = [], 0
    encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    for chunk in encoder.iterencode(handoff):
        size += len(chunk)
        if size > (20_000_000 if recommendation else INPUT_LIMIT):
            raise ValueError("handoff_size_limit")
        chunks.append(chunk)
    raw = "".join(chunks).encode("ascii")
    digest = hashlib.sha256(raw).hexdigest()
    return {"status": "ready", "handoff": json.loads(raw), "file_id": None,
            "sha256": digest, "payload_sha256": digest, "input_mode": "structured",
            "canonicalization": "canonical-json/1", "schema": schema}


def structured_dispatch(prepared, *, recommendation=False):
    """Recompute at the submit boundary; never trust a stored hash alone."""
    checked = prepare_handoff(prepared.get("handoff"), recommendation=recommendation)
    for key in ("status", "file_id", "sha256", "payload_sha256", "input_mode", "canonicalization", "schema"):
        if key not in prepared or prepared[key] != checked[key]:
            raise ValueError("handoff_descriptor_mismatch")
    return {"task": {"intent": "dispatch", "payload": {"parts": [
        {"type": "form", "slot": "enrichment_handoff" if recommendation else "triage_handoff",
         "params": {"enrichment" if recommendation else "handoff": checked["handoff"]}}
    ]}}}


def verify_structured_receipt(receipt, expected, *, recommendation=False):
    """No legacy file-receipt downgrade after a structured submission."""
    if not isinstance(receipt, dict):
        raise ValueError("receipt_mismatch")
    digest = expected.get("payload_sha256")
    if (expected.get("input_mode") != "structured" or expected.get("file_id") is not None
            or expected.get("sha256") != digest or expected.get("canonicalization") != "canonical-json/1"
            or expected.get("schema") != ("alert-enrichment/1" if recommendation else "alert-indicators/3")
            or not isinstance(digest, str) or len(digest) != 64
            or any(c not in "0123456789abcdef" for c in digest)):
        raise ValueError("invalid_expected_receipt")
    for key, value in (("file_id", None), ("input_mode", "structured"),
                       ("schema", "alert-enrichment/1" if recommendation else "alert-indicators/3"), ("canonicalization", "canonical-json/1"),
                       ("sha256", digest), ("payload_sha256", digest)):
        if key not in receipt or receipt[key] != value:
            raise ValueError("receipt_mismatch")
