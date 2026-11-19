"""Bounded finite JSON snapshot for the explicit enrichment_handoff form."""
import hashlib
import json
import math

if __package__:
    from .core import LIMIT, ValidationError, packets, require
else:
    from core import LIMIT, ValidationError, packets, require


def canonical_payload(data):
    """canonical-json/1: sorted compact ASCII JSON, no newline; not RFC 8785."""
    nodes = 0

    def check(value, depth=0):
        nonlocal nodes
        nodes += 1
        require(nodes <= 2_000_000 and depth <= 40, "structure_limit")
        kind = type(value)
        if kind is str:
            require(len(value) <= 10000, "string_limit")
        elif kind is dict:
            for key, child in value.items():
                require(type(key) is str, "invalid_json_key")
                check(key, depth + 1)
                check(child, depth + 1)
        elif kind is list:
            for child in value:
                check(child, depth + 1)
        elif kind is float:
            require(math.isfinite(value), "nonfinite_number")
        else:
            require(value is None or kind in (bool, int), "invalid_json_type")

    try:
        check(data)
        size, chunks = 0, []
        encoder = json.JSONEncoder(sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
        for chunk in encoder.iterencode(data):
            size += len(chunk)
            require(size <= LIMIT, "input_too_large")
            chunks.append(chunk)
        raw = "".join(chunks).encode("ascii")
        snapshot = json.loads(raw)
        # Same joins, status/coverage validation and per-incident packet budgets
        # as managed-file input, before any model or file write.
        packets(snapshot)
    except (ValueError, TypeError, RecursionError, OverflowError, KeyError):
        raise ValidationError("invalid_structured_enrichment") from None
    return snapshot, hashlib.sha256(raw).hexdigest()
