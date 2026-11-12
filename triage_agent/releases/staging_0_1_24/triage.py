"""Deterministic UEBA triage pipeline. No network access in this module."""
from __future__ import annotations

import argparse
import asyncio
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
import math
import time
from pathlib import Path
import re
from urllib.parse import urlsplit

FIXTURE = "ueba_findings_sim_run2_2026-11-03.jsonl"
DETECTORS = {
    "fanout": "distinct external destinations",
    "protocol_mix": "distinct destinations over one protocol",
    "egress_volume": "distinct destinations of uploads of 100 MB or more",
    "geo_spread": "distinct destination countries",
    "company_spread": "distinct destination companies",
    "fan_in": "distinct internal sources",
    "site_volume": "distinct active hosts",
}
PRIORITIES = {"high": 0, "medium": 1, "low": 2, "unknown": 3}
DOMAIN_FIELDS = {"domain", "domain_name", "hostname", "dns_name", "query_name", "url", "url_host"}
REGISTRATION_FIELDS = {"asn", "registered_organization", "network_range", "registration_date"}
IOC_FIELDS = ("time_window", "src", "dst", "protocol", "bytes_sent", "bytes_received", "country", "company", "src_site")
ASSUMPTION = "POC assumption: bytes_sent and bytes_received are relative to src. Sample sums are not verified incident or capture totals; flow IDs and counter semantics are absent."


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    normalized = re.sub(r"([+-]\d{2})(\d{2})$", r"\1:\2", value.replace("Z", "+00:00"))
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp requires timezone")
    return parsed.astimezone(timezone.utc).isoformat()


def number(value, name, nullable=False, minimum=None):
    if value is None and nullable:
        return
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")


def text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")


def validate_finding(f):
    if not isinstance(f, dict) or f.get("schema") != "swoop-ueba-finding/1":
        raise ValueError("unsupported finding schema")
    for key in ("finding_id", "incident_key", "source"):
        text(f.get(key), key)
    entity = f.get("entity")
    if not isinstance(entity, dict) or entity.get("type") not in {"host", "external_service", "site"}:
        raise ValueError("unsupported entity")
    text(entity.get("id"), "entity.id")
    if entity.get("site") is not None:
        text(entity["site"], "entity.site")
    window = f.get("time_window", {})
    if utc(window["start"]) > utc(window["end"]):
        raise ValueError("reversed time window")
    detector = f.get("detector")
    if detector not in DETECTORS or f.get("measures") != DETECTORS[detector]:
        raise ValueError("unsupported detector/measure combination")
    if detector == "protocol_mix":
        text(entity.get("protocol"), "entity.protocol")
    number(f.get("observed"), "observed", minimum=0)
    baseline = f.get("baseline")
    if not isinstance(baseline, dict):
        raise ValueError("baseline must be an object")
    number(baseline.get("mean"), "baseline.mean", minimum=0)
    number(baseline.get("std_dev"), "baseline.std_dev", minimum=0)
    if type(baseline.get("windows")) is not int or baseline["windows"] < 1:
        raise ValueError("baseline.windows must be a positive integer")
    if type(baseline.get("zero_variance")) is not bool:
        raise ValueError("baseline.zero_variance must be boolean")
    if baseline["zero_variance"] != (baseline["std_dev"] == 0):
        raise ValueError("inconsistent baseline zero variance")
    number(f.get("z_score"), "z_score", nullable=True)
    if baseline["zero_variance"] and f.get("z_score") is not None:
        raise ValueError("zero variance requires null z_score")
    number(f.get("normalcy_score"), "normalcy_score", minimum=0)
    if f["normalcy_score"] > 1:
        raise ValueError("normalcy_score exceeds 1")
    if not isinstance(f.get("evidence"), list):
        raise ValueError("evidence must be a list")
    for row in f["evidence"]:
        if not isinstance(row, dict):
            raise ValueError("evidence row must be an object")
        utc(row.get("time"))
        for key in ("src", "dst", "protocol"):
            text(row.get(key), f"evidence.{key}")
        for key in ("bytes_sent", "bytes_received"):
            number(row.get(key), f"evidence.{key}", minimum=0)
        number(row.get("bytes_sent_z_score"), "bytes_sent_z_score", nullable=True)
        for key in ("company", "country", "src_site"):
            if row.get(key) is not None:
                text(row[key], f"evidence.{key}")
    related = f.get("related_entities", [])
    if not isinstance(related, list) or any(not isinstance(x, (str, dict)) for x in related):
        raise ValueError("related_entities must be a list of strings or objects")


def parse_jsonl(content):
    records, errors, versions = [], [], defaultdict(list)
    input_format = "jsonl"
    # Parse whole JSON first; malformed JSONL still gets per-line error handling.
    try:
        whole = json.loads(content)
    except (ValueError, TypeError):
        whole = None
    entries = None
    if isinstance(whole, list):
        entries, input_format = whole, "json_array"
    elif isinstance(whole, dict):
        if "findings" in whole and "schema" not in whole:
            if set(whole) != {"findings"} or not isinstance(whole["findings"], list):
                entries, input_format = [None], "invalid_json_wrapper"
            else:
                entries, input_format = whole["findings"], "json_findings_wrapper"
        else:
            entries, input_format = [whole], "json_object"
    if entries is not None:
        source_entries = [(i, json.dumps(f)) for i, f in enumerate(entries, 1)]
    else:
        source_entries = [(i, raw) for i, raw in enumerate(content.splitlines(), 1) if raw.strip()]
    if len(source_entries) > 100:
        return [], {"nonempty_lines": len(source_entries), "accepted_findings": 0, "accepted_source_lines": 0,
                    "duplicate_lines": 0, "input_format": input_format,
                    "source_location_kind": "line" if input_format == "jsonl" else "record_index_1_based",
                    "errors": [{"kind": "record_limit", "error": "More than 100 records; input refused, not truncated."}]}
    nonempty = 0
    for line, raw in source_entries:
        if not raw.strip():
            continue
        nonempty += 1
        try:
            f = json.loads(raw, parse_constant=lambda x: (_ for _ in ()).throw(ValueError("nonfinite JSON")))
            validate_finding(f)
            versions[f["finding_id"]].append((line, f))
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            errors.append({"line": line, "kind": "invalid_record", "error": str(exc)})
    duplicates = 0
    for finding_id, entries in versions.items():
        if len({canonical(f) for _, f in entries}) > 1:
            errors.append({"lines": [n for n, _ in entries], "finding_id": finding_id,
                           "kind": "conflicting_id", "error": "All versions quarantined"})
            continue
        duplicates += len(entries) - 1
        records.append({"finding": entries[0][1], "source_lines": [n for n, _ in entries]})
    records.sort(key=lambda x: x["source_lines"][0])
    return records, {"nonempty_lines": nonempty, "accepted_findings": len(records),
                     "input_format": input_format,
                     "source_location_kind": "line" if input_format == "jsonl" else "record_index_1_based",
                     "accepted_source_lines": sum(len(r["source_lines"]) for r in records),
                     "duplicate_lines": duplicates, "errors": errors}


def normalize_domain(raw, is_url=False):
    text(raw, "domain")
    value = urlsplit(raw).hostname if is_url else raw
    if not value:
        raise ValueError("URL has no hostname")
    value = value.rstrip(".").encode("idna").decode("ascii").lower()
    try:
        ipaddress.ip_address(value)
    except ValueError:
        pass
    else:
        raise ValueError("IP literal is not a domain")
    if len(value) > 253 or "." not in value or not all(
        re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
        for label in value.split(".")
    ) or not re.search(r"[a-z]", value.split(".")[-1]):
        raise ValueError("invalid domain syntax")
    return value


def walk(value, path=""):
    if isinstance(value, dict):
        for key, child in value.items():
            childpath = f"{path}.{key}" if path else key
            yield key, child, childpath
            yield from walk(child, childpath)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from walk(child, f"{path}[{i}]")


def extract_ioc_observations(records):
    """Copy the requested fields exactly, with per-occurrence provenance.

    Do not collapse different evidence rows just because their selected fields
    match. Shared exact rows keep all references without becoming corroboration.
    """
    rows, issues = {}, []
    for record in records:
        f = record["finding"]
        for index, evidence in enumerate(f["evidence"]):
            key = canonical({"time_window": f["time_window"], "evidence": evidence})
            values = {"time_window": deepcopy(f["time_window"]),
                      **{field: deepcopy(evidence.get(field)) for field in IOC_FIELDS[1:]}}
            observation = rows.setdefault(key, {**values, "occurrences": [],
                "interpretation": "Candidate IOC observation for investigation, not proof of compromise; country/company are supplied unverified destination labels."})
            missing = [field for field in IOC_FIELDS[1:] if field not in evidence]
            nulls = [field for field in IOC_FIELDS[1:] if field in evidence and evidence[field] is None]
            paths = {field: ("time_window" if field == "time_window" else f"evidence[{index}].{field}")
                     for field in IOC_FIELDS if field == "time_window" or field in evidence}
            for line in record["source_lines"]:
                observation["occurrences"].append({"finding_id": f["finding_id"], "source_line": line,
                    "evidence_path": f"evidence[{index}]", "field_paths": paths,
                    "missing_fields": missing, "null_fields": nulls})
            if missing or nulls:
                issues.append({"kind": "incomplete_ioc_observation", "finding_id": f["finding_id"],
                               "source_lines": record["source_lines"], "evidence_path": f"evidence[{index}]",
                               "missing_fields": missing, "null_fields": nulls})
    return list(rows.values()), issues


def indicator_inventory(records):
    inventory, issues = {}, []

    def add(kind, raw, record, path, role, enrichment=None):
        try:
            if kind == "ip":
                ip = ipaddress.ip_address(raw)
                normalized = str(ip)
            else:
                normalized = normalize_domain(raw, path.split(".")[-1] == "url")
        except (ValueError, TypeError, UnicodeError):
            issues.append({"kind": "invalid_indicator", "finding_id": record["finding"]["finding_id"],
                           "source_lines": record["source_lines"], "field_path": path, "raw_value": raw})
            return
        item = inventory.setdefault((kind, normalized), {
            "type": kind, "raw_value": raw, "normalized_value": normalized,
            "roles": [], "occurrences": [], "supplied_enrichment": [], "enrichment_conflict": False,
        })
        if kind == "ip":
            ip = ipaddress.ip_address(normalized)
            item["address_classification"] = {
                "is_private": ip.is_private, "is_global": ip.is_global,
                "is_loopback": ip.is_loopback, "is_reserved": ip.is_reserved,
                "ownership": "unknown; address classification does not establish network ownership",
            }
        if role not in item["roles"]:
            item["roles"].append(role)
        for line in record["source_lines"]:
            occurrence = {"finding_id": record["finding"]["finding_id"], "source_line": line,
                          "field_path": path, "role": role, "raw_value": raw,
                          "supplied_enrichment": enrichment or []}
            item["occurrences"].append(occurrence)
        for label in enrichment or []:
            sourced = dict(label, finding_id=record["finding"]["finding_id"], source_lines=record["source_lines"])
            if sourced not in item["supplied_enrichment"]:
                item["supplied_enrichment"].append(sourced)

    for record in records:
        f = record["finding"]
        entity = f["entity"]
        if entity["type"] != "site":
            try:
                ipaddress.ip_address(entity["id"])
                add("ip", entity["id"], record, "entity.id", "entity")
            except ValueError:
                if ":" in entity["id"] or re.fullmatch(r"[\d.]+", entity["id"]):
                    add("ip", entity["id"], record, "entity.id", "entity")
        for i, row in enumerate(f["evidence"]):
            labels = [{"attribute": k, "value": row[k], "source_path": f"evidence[{i}].{k}",
                       "verification": "supplied, unverified"}
                      for k in sorted({"company", "country"} | REGISTRATION_FIELDS) if row.get(k) is not None]
            add("ip", row["src"], record, f"evidence[{i}].src", "source")
            add("ip", row["dst"], record, f"evidence[{i}].dst", "destination", labels)
        for i, related in enumerate(f.get("related_entities", [])):
            value = related.get("id") if isinstance(related, dict) else related
            if isinstance(related, dict) and related.get("type") == "site":
                continue
            if isinstance(value, str):
                try:
                    ipaddress.ip_address(value)
                    candidate = True
                except ValueError:
                    candidate = ":" in value or bool(re.fullmatch(r"[\d.]+", value))
                if candidate:
                    add("ip", value, record, f"related_entities[{i}]" + (".id" if isinstance(related, dict) else ""), "related")
        for key, value, path in walk(f):
            if key in DOMAIN_FIELDS:
                add("domain", value, record, path, "url_host" if key == "url" else key)
    for item in inventory.values():
        labels = defaultdict(set)
        for label in item["supplied_enrichment"]:
            labels[label["attribute"]].add(canonical(label["value"]))
        if any(len(values) > 1 for values in labels.values()):
            item["enrichment_conflict"] = True
            issues.append({"kind": "conflicting_enrichment", "indicator": item["normalized_value"]})
    observations, observation_issues = extract_ioc_observations(records)
    issues.extend(observation_issues)
    return {"ips": [v for (kind, _), v in sorted(inventory.items()) if kind == "ip"],
            "domains": [v for (kind, _), v in sorted(inventory.items()) if kind == "domain"],
            "ioc_fields": list(IOC_FIELDS), "observations": observations}, issues


def group_findings(records):
    groups = defaultdict(list)
    for record in records:
        f = record["finding"]
        e, w = f["entity"], f["time_window"]
        groups[(e["type"], e["id"], e.get("site"), f["incident_key"], utc(w["start"]), utc(w["end"]))].append(record)
    return list(groups.values())


def summarize(records):
    first = records[0]["finding"]
    indicators, issues = indicator_inventory(records)
    rows, metrics, severities = {}, [], []
    for record in records:
        f = record["finding"]
        severity = f.get("severity")
        severities.append({"finding_id": f["finding_id"], "severity": severity})
        if severity not in {"high", "medium", "low"}:
            issues.append({"kind": "unknown_severity", "finding_id": f["finding_id"]})
        metrics.append({**{k: deepcopy(f.get(k)) for k in ("finding_id", "detector", "measures", "observed", "baseline", "z_score", "normalcy_score", "severity")},
                        "entity": f["entity"], "source_lines": record["source_lines"],
                        "supplied_evidence_rows": len(f["evidence"])})
        for i, row in enumerate(f["evidence"]):
            entry = rows.setdefault(canonical(row), {"row": row, "occurrences": []})
            entry["occurrences"].extend({"finding_id": f["finding_id"], "source_line": line,
                                         "field_path": f"evidence[{i}]"} for line in record["source_lines"])
            direction = row.get("byte_direction")
            if direction is not None and direction != "relative_to_src":
                issues.append({"kind": "contradictory_byte_direction", "finding_id": f["finding_id"], "field_path": f"evidence[{i}].byte_direction"})
            if not (utc(f["time_window"]["start"]) <= utc(row["time"]) <= utc(f["time_window"]["end"])):
                issues.append({"kind": "evidence_outside_window", "finding_id": f["finding_id"], "field_path": f"evidence[{i}].time"})
    evidence = list(rows.values())
    issues.append({"kind": "byte_direction_assumed", "detail": ASSUMPTION})
    valid = [s["severity"] for s in severities if s["severity"] in PRIORITIES]
    priority = min(valid, key=lambda s: PRIORITIES[s]) if valid else "unknown"
    summary = {
        "scope": "supplied evidence only; overlapping detectors are not independent corroboration",
        "evidence_occurrences": sum(len(x["occurrences"]) for x in evidence),
        "unique_exact_rows": len(evidence),
        "distinct_sample_sources": len({r["row"]["src"] for r in evidence}),
        "distinct_sample_destinations": len({r["row"]["dst"] for r in evidence}),
        "protocols": sorted({r["row"]["protocol"] for r in evidence}),
        "source_sites": sorted({r["row"]["src_site"] for r in evidence if r["row"].get("src_site")}),
        "sample_bytes_sent_sum": sum(r["row"]["bytes_sent"] for r in evidence),
        "sample_bytes_received_sum": sum(r["row"]["bytes_received"] for r in evidence),
        "largest_sent_byte_rows": sorted(evidence, key=lambda r: r["row"]["bytes_sent"], reverse=True)[:3],
        "byte_direction_assumption": ASSUMPTION,
        "evidence": evidence,
        "coverage": "Rows are samples. Compare detector metrics in their own units; do not add observed counts across detectors or infer completeness from related_entities.",
    }
    return {"incident_key": first["incident_key"],
            "entity": {k: first["entity"].get(k) for k in ("type", "id", "site")},
            "time_window": first["time_window"],
            "time_window_utc": {k: utc(v) for k, v in first["time_window"].items()},
            "source": sorted({r["finding"]["source"] for r in records}),
            "synthetic": all(r["finding"]["source"] == "swoop/valhalla/simulated" for r in records),
            "finding_ids": [r["finding"]["finding_id"] for r in records],
            "source_lines": sorted(n for r in records for n in r["source_lines"]),
            "original_severities": severities, "review_priority": priority,
            "priority_rule": "Highest supported supplied severity; unknown values are flagged, not scored.",
            "disposition": "needs_review", "detector_metrics": metrics, "sample_summary": summary,
            "indicators": indicators, "data_quality_issues": issues}


async def analyze(content, client, progress=None):
    records, run = parse_jsonl(content)
    results = []
    groups = group_findings(records)
    prepared = [(group, summarize(group)) for group in groups]
    if progress:
        progress(f"Identified {len(records)} findings across {len(groups)} incident groups.")
        if run["errors"]:
            progress(f"Found {len(run['errors'])} input issues; valid findings will still be reviewed.")
    # Sequential by design: one bounded call per group, no retries or agents delegating.
    for index, (group, result) in enumerate(prepared, 1):
        if progress:
            progress(f"Reviewing incident group {index} of {len(groups)}…")
        started = time.monotonic()
        stage = "model_call"
        try:
            if getattr(client, "extraction_only", False):
                raise NarrativeDeferred()
            narrative = await client.analyze(group, result)
            if __package__:
                from .agent import validate_response, validate_context_response
            else:
                from agent import validate_response, validate_context_response
            stage = "response_validation"
            validator = validate_context_response if getattr(client, "response_mode", None) == "context_only" else validate_response
            result.update(validator(narrative, group, result))
            result["analysis_status"] = "completed"
        except Exception as exc:
            # Never persist provider error strings: they can contain request URLs or credentials.
            if hasattr(exc, "field") and hasattr(exc, "code"):
                stage = "response_validation"
            code = getattr(exc, "code", None) if stage == "response_validation" else None
            if not code:
                code = "timeout" if type(exc).__name__ in {"APITimeoutError", "ReadTimeout", "TimeoutError"} else ("validation_rejected" if stage == "response_validation" else "model_request_failed")
            result.update(summary="", key_evidence=[], possible_explanations=[], limitations=[],
                          recommended_next_steps=[], highlighted_indicators=[], analysis_status="failed",
                          analysis_error={"stage": stage, "type": type(exc).__name__, "code": code,
                                          "field": getattr(exc, "field", None),
                                          "message": str(exc) if stage == "response_validation" and isinstance(exc, ValueError) else "Narrative call or validation failed; deterministic results preserved."})
        if getattr(client, "extraction_only", False):
            result["analysis_error"] = {"stage": "policy", "type": "NarrativeDeferred", "code": "narrative_deferred",
                                        "field": None, "message": "Narrative intentionally deferred to Recommendation; no triage inference attempted."}
        result["analysis_duration_seconds"] = round(time.monotonic() - started, 3)
        results.append(result)
        if progress and result["analysis_status"] == "failed":
            progress(f"Context for incident group {index} was unavailable; extracted indicators were retained.")
    results.sort(key=lambda r: (PRIORITIES[r["review_priority"]], r["incident_key"]))
    run.update(incident_groups=len(results), completed=sum(r["analysis_status"] == "completed" for r in results),
               failed=sum(r["analysis_status"] == "failed" for r in results),
               input_sha256=hashlib.sha256(content.encode()).hexdigest(),
               model=getattr(client, "model_name", "stub"))
    run["status"] = "partial" if run["errors"] or run["failed"] else ("empty" if not results else "completed")
    run["analysis_failures"] = [{"incident_key": r["incident_key"], "duration_seconds": r["analysis_duration_seconds"], **r["analysis_error"]}
                                for r in results if r["analysis_status"] == "failed"]
    return {"schema": "alert-triage-results/1", "run": run, "results": results}


class NarrativeDeferred(Exception):
    """Existing v3 unavailable-context representation; not a provider failure."""


class ExtractionOnlyClient:
    extraction_only = True
    model_name = "none:deterministic-extraction"


def safe_md(value):
    # Alert strings are data, not Markdown/HTML or active links.
    return re.sub(r"([\\`*_{}\[\]()<>#!|])", r"\\\1", str(value)).replace("\n", " ")


def render_report(data):
    run = data["run"]
    lines = ["# Alert triage report", "", f"Run: {run['status']}; {run['accepted_findings']} accepted findings; {run['incident_groups']} groups; {run['failed']} narrative failures.",
             "", "Investigation leads only. Supplied company/country labels are unverified; scores are not probabilities of compromise.",
             "", ASSUMPTION]
    for error in run["errors"]:
        lines.append("- Input error: " + safe_md(json.dumps(error)))
    for r in data["results"]:
        lines += ["", f"## {safe_md(r['review_priority'].upper())}: {safe_md(r['entity']['id'])}",
                  f"Incident: {safe_md(r['incident_key'])}; disposition: needs_review; analysis: {r['analysis_status']}; synthetic: {r['synthetic']}.",
                  "", safe_md(r["summary"]) if r["summary"] else "Narrative unavailable; deterministic facts retained.", "", "### Detector facts"]
        for metric in r["detector_metrics"]:
            lines.append(f"- {safe_md(metric['detector'])}: {metric['observed']} {safe_md(metric['measures'])}; baseline mean {metric['baseline']['mean']}; z-score {metric['z_score']}. Finding {metric['finding_id']}.")
        s = r["sample_summary"]
        lines.append(f"- Supplied sample: {s['unique_exact_rows']} unique exact rows from {s['evidence_occurrences']} occurrences; {s['distinct_sample_sources']} sources; {s['distinct_sample_destinations']} destinations; sent-byte sample sum {s['sample_bytes_sent_sum']} (not an incident total).")
        if not r["indicators"]["domains"]:
            lines.append("- No domains supplied.")
        lines += ["", "### Extracted IOC fields", "",
                  "Candidate observations only; repeated evidence references are not independent corroboration.",
                  "Missing or null values are shown as unknown; zero bytes remain zero.", "",
                  "| Time window | src | dst | protocol | bytes_sent | bytes_received | country | company | src_site | References |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for observation in r["indicators"]["observations"]:
            cells = []
            for field in IOC_FIELDS:
                value = observation[field]
                if field == "time_window":
                    value = value["start"] + " → " + value["end"]
                cells.append(safe_md("unknown" if value is None else value))
            refs = "; ".join(f"{o['finding_id']}:{o['evidence_path']} (source {o['source_line']})"
                             for o in observation["occurrences"])
            lines.append("| " + " | ".join([*cells, safe_md(refs)]) + " |")
        lines += ["", "### Highlighted indicators"]
        highlighted = set(r.get("highlighted_indicators", []))
        for indicator in r["indicators"]["ips"] + r["indicators"]["domains"]:
            if indicator["normalized_value"] in highlighted:
                labels = sorted({str(e["attribute"]) + "=" + str(e["value"]) for e in indicator["supplied_enrichment"]})
                lines.append("- " + safe_md(indicator["normalized_value"] + ": " + ", ".join(indicator["roles"]) + "; supplied unverified labels: " + (", ".join(labels) or "unknown")))
        for title, key in (("Key evidence", "key_evidence"), ("Hypotheses—not conclusions", "possible_explanations"), ("Limitations", "limitations"), ("Next analyst checks", "recommended_next_steps")):
            lines += ["", "### " + title]
            for item in r[key]:
                lines.append("- " + safe_md(item if isinstance(item, str) else f"{item['claim']} [{item['finding_id']}:{item['field_path']}]"))
        lines += ["", "### Data-quality notes"]
        lines.extend("- " + safe_md(json.dumps(issue)) for issue in r["data_quality_issues"])
        if r.get("analysis_error"):
            lines.append("- " + safe_md(json.dumps(r["analysis_error"])))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=FIXTURE)
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--stub", action="store_true", help="Explicit deterministic test narrative, not live analysis")
    parser.add_argument("--audit-export", action="store_true", help="Also write the detailed version-2 indicator export")
    args = parser.parse_args()
    if __package__:
        from .agent import LiveClient, StubClient
    else:
        from agent import LiveClient, StubClient
    data = asyncio.run(analyze(Path(args.input).read_text(), StubClient() if args.stub else LiveClient()))
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "triage_results.json").write_text(json.dumps(data, indent=2, allow_nan=False) + "\n")
    (out / "triage_report.md").write_text(render_report(data))
    if __package__:
        from .export import build_indicator_export
    else:
        from export import build_indicator_export
    (out / "extracted_indicators.json").write_text(json.dumps(build_indicator_export(data), separators=(",", ":"), allow_nan=False) + "\n")
    if args.audit_export:
        if __package__:
            from .export import build_audit_export
        else:
            from export import build_audit_export
        (out / "extracted_indicators.audit.json").write_text(json.dumps(build_audit_export(data), indent=2, allow_nan=False) + "\n")
    print(json.dumps(data["run"], indent=2))
    return 0 if data["run"]["status"] == "completed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
