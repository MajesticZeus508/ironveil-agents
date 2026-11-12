"""Strict, dependency-free interchange validation and normalization."""
import hashlib
import ipaddress
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast


class ContractError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ContractError(message)


def text(value):
    require(isinstance(value, str) and 0 < len(value) <= 10_000, "invalid_string")
    return value


def integer(value, minimum=0, maximum=2**63 - 1):
    require(type(value) is int and minimum <= value <= maximum, "invalid_integer")
    return value


def timestamp(value):
    text(value)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(result.tzinfo is not None, "timezone_required")
        return result.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ContractError("invalid_timestamp") from None


def window(value):
    require(isinstance(value, dict), "invalid_window")
    start, end = timestamp(value.get("start")), timestamp(value.get("end"))
    require(start <= end, "reversed_window")
    return start, end


def ip(value):
    text(value)
    require("%" not in value, "scoped_ip_not_supported")
    try:
        return str(ipaddress.ip_address(value))
    except ValueError:
        raise ContractError("invalid_ip") from None


def domain(value):
    try:
        result = text(value).removesuffix(".").encode("idna").decode("ascii").lower()
    except UnicodeError:
        raise ContractError("invalid_domain") from None
    require(len(result) <= 253 and "." in result, "invalid_domain")
    require(all(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", p)
                for p in result.split(".")), "invalid_domain")
    try:
        ipaddress.ip_address(result)
    except ValueError:
        return result
    raise ContractError("domain_is_ip")


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def load(path, limit=10_000_000):
    with Path(path).open("rb") as stream:
        raw = stream.read(limit + 1)
    return parse_bytes(raw, limit)


def parse_bytes(raw, limit=10_000_000):
    """Same strict parser for filesystem and managed-file byte inputs."""
    require(len(raw) <= limit, "input_too_large")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs,
                           parse_constant=lambda _: require(False, "nonfinite_number"))
        _bounds(value)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise ContractError("invalid_json") from None
    return value, hashlib.sha256(raw).hexdigest()


def _bounds(value, depth=0):
    require(depth <= 40, "nesting_limit")
    if isinstance(value, str):
        require(len(value) <= 10_000, "string_limit")
    elif isinstance(value, (dict, list)):
        for item in (list(value.keys()) + list(value.values()) if isinstance(value, dict) else value):
            _bounds(item, depth + 1)
    elif isinstance(value, float):
        import math
        require(math.isfinite(value), "nonfinite_number")


def validate_handoff(data: Any):
    require(isinstance(data, dict) and data.get("schema") == "alert-indicators/3", "unsupported_handoff")
    for key in ("source", "extraction", "context_provenance"):
        require(isinstance(data.get(key), dict), "invalid_" + key)
    require(data["source"].get("source_location_kind") in ("line", "record_index_1_based"), "invalid_source_location")
    require(data["extraction"].get("status") in ("completed", "partial", "empty"), "invalid_extraction_status")
    require(isinstance(data["extraction"].get("errors"), list), "invalid_extraction_errors")
    incidents, rows = data.get("incidents"), data.get("indicators")
    require(isinstance(incidents, list) and len(incidents) <= 1000, "incident_limit")
    require(isinstance(rows, list) and len(rows) <= 10_000, "observation_limit")
    incidents, rows = cast(list, incidents), cast(list, rows)
    by_id = {}
    for incident in incidents:
        require(isinstance(incident, dict), "invalid_incident")
        key = text(incident.get("id"))
        require(key not in by_id, "duplicate_incident_id")
        window(incident.get("time_window"))
        require(isinstance(incident.get("entity"), dict), "invalid_entity")
        require(incident.get("analysis_status") in ("completed", "failed"), "invalid_analysis_status")
        require(incident.get("context_status") in ("available", "unavailable"), "invalid_context_status")
        by_id[key] = incident
    ids = set()
    for row in rows:
        require(isinstance(row, dict), "invalid_observation")
        key = text(row.get("id"))
        require(key not in ids, "duplicate_observation_id")
        ids.add(key)
        require(isinstance(row.get("incident_id"), str) and row["incident_id"] in by_id, "dangling_incident")
        if "time_window" in row:
            window(row["time_window"])
        for field in ("src", "dst"):
            require(field in row, "missing_endpoint")
            if row[field] is not None:
                ip(row[field])
        for field in ("protocol", "country", "company", "src_site"):
            require(field in row, "missing_observation_field")
            if row[field] is not None:
                text(row[field])
        for field in ("bytes_sent", "bytes_received"):
            require(field in row, "missing_byte_field")
            if row[field] is not None:
                integer(row[field])
        require(isinstance(row.get("refs"), list) and bool(row["refs"]), "missing_refs")
        for ref in row["refs"]:
            require(isinstance(ref, dict), "invalid_ref")
            text(ref.get("finding_id"))
            integer(ref.get("source"), 1)
            integer(ref.get("evidence_index"))
            for field in ("missing_fields", "null_fields"):
                if field in ref:
                    require(isinstance(ref[field], list) and all(isinstance(x, str) for x in ref[field]), "invalid_field_metadata")
    for key, count in (("incident_groups", len(incidents)), ("observation_count", len(rows))):
        require(type(data["extraction"].get(key)) is int and data["extraction"][key] == count, "extraction_count_mismatch")
    integer(data["extraction"].get("accepted_findings"))
    return by_id


OPTIONAL = {"dst_domain": domain, "dst_asn": lambda x: integer(x, 1, 4294967295),
            "dst_registered_org": text}


def validate_context(data: Any, observation_ids):
    if data is None:
        return {}
    require(isinstance(data, dict) and data.get("schema") == "enrichment-context/1", "unsupported_context")
    require(isinstance(data.get("observations"), list), "invalid_context_observations")
    result = {}
    for row in data["observations"]:
        require(isinstance(row, dict), "invalid_context_row")
        key = text(row.get("observation_id"))
        require(key in observation_ids and key not in result, "invalid_context_join")
        require(set(row) <= {"observation_id", "source", *OPTIONAL}, "unsupported_context_field")
        text(row.get("source"))
        result[key] = {k: normalize(row[k]) for k, normalize in OPTIONAL.items() if k in row}
    return result
