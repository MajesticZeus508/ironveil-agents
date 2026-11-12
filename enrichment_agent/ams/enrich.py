"""Offline historical enrichment CLI; adapters own access, code owns results."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import html
import ipaddress
import json
from pathlib import Path
import re
import sys

if __package__:
    from .contracts import (ContractError, identity, integer, ip, load, require,
                            timestamp, validate_context, validate_handoff, window)
    from .history import LocalHistory, UnconfiguredAWSHistory
else:
    from contracts import (ContractError, identity, integer, ip, load, require,
                           timestamp, validate_context, validate_handoff, window)
    from history import LocalHistory, UnconfiguredAWSHistory


def plan_queries(handoff, context=None, lookback_days=30):
    integer(lookback_days, 1, 3650)
    incidents = validate_handoff(handoff)
    extras = validate_context(context, {r["id"] for r in handoff["indicators"]})
    queries = {}

    def add(incident_id, kind, criteria, row_id=None, missing=None):
        end, _ = window(incidents[incident_id]["time_window"])
        try:
            start = end - timedelta(days=lookback_days)
        except OverflowError:
            raise ContractError("lookback_out_of_range") from None
        base = {"incident_id": incident_id, "kind": kind, "criteria": criteria,
                "window": {"start": start.isoformat(), "end_exclusive": end.isoformat()}}
        if missing:
            base["missing_input"] = missing
        key = identity(["history-query/1", base])
        if key not in queries:
            require(len(queries) < 100_000, "query_limit")
            queries[key] = {"query_id": key, **base, "observation_ids": []}
        if row_id is not None:
            queries[key]["observation_ids"].append(row_id)

    for row in handoff["indicators"]:
        inc, rid = row["incident_id"], row["id"]
        for field in ("src", "dst"):
            if row[field] is not None:
                add(inc, "ip_prevalence", {"endpoint_ip": ip(row[field])}, rid)
        for field, historical_field in (("country", "dst_country"), ("company", "dst_company")):
            if row[field] is not None:
                add(inc, "attribute_prevalence", {historical_field: row[field]}, rid)
        for field, value in extras.get(rid, {}).items():
            add(inc, "domain_prevalence" if field == "dst_domain" else "attribute_prevalence", {field: value}, rid)
        needed = ("src", "dst", "protocol", "src_site")
        missing = [k for k in needed if row[k] is None]
        criteria = {k: (ip(row[k]) if k in ("src", "dst") else row[k].upper() if k == "protocol" else row[k])
                    for k in needed if row[k] is not None}
        add(inc, "directed_activity_tuple", criteria, rid, missing)
    for inc, incident in incidents.items():
        entity_id = incident["entity"].get("id")
        try:
            normalized = ip(entity_id)
        except ContractError:
            continue
        add(inc, "ip_prevalence", {"endpoint_ip": normalized})
    for query in queries.values():
        query["observation_ids"] = sorted(set(query["observation_ids"]))
        if query["kind"] == "ip_prevalence":
            value = query["criteria"]["endpoint_ip"]
            query["indicator_key"] = identity(["indicator/1", "ip", value])
            query["address_classification"] = "global" if ipaddress.ip_address(value).is_global else "non_global"
    return sorted(queries.values(), key=lambda q: q["query_id"])


def enrich(handoff, adapter, *, context=None, lookback_days=30, sample_limit=5,
           handoff_sha256=None, context_sha256=None):
    integer(sample_limit, 1, 100)
    plan = plan_queries(handoff, context, lookback_days)
    results = []
    for query in plan:
        if query.get("missing_input"):
            outcome = {"status": "insufficient_input", "search_complete": False,
                       "matched_record_count": None, "first_seen": None, "last_seen": None,
                       "samples": [], "samples_truncated": False}
        else:
            try:
                outcome = adapter.search(query["criteria"], timestamp(query["window"]["start"]),
                                         timestamp(query["window"]["end_exclusive"]), sample_limit)
            except Exception:
                # Adapter/provider exception text may contain credentials or query data.
                outcome = {"status": "error", "search_complete": False,
                           "error_code": "history_query_failed", "matched_record_count": None,
                           "first_seen": None, "last_seen": None, "samples": [], "samples_truncated": False}
        results.append({**query, **outcome})
    partial = (handoff["extraction"]["status"] == "partial" or bool(handoff["extraction"]["errors"])
               or bool(adapter.errors) or any(not r["search_complete"] for r in results))
    status = "empty" if not results and not partial else "partial" if partial else "completed"
    return {
        "schema": "alert-enrichment/1", "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": deepcopy(handoff), "input_sha256": handoff_sha256,
        "supplemental_context": deepcopy(context), "context_sha256": context_sha256,
        "source": deepcopy(adapter.metadata),
        "run": {"status": status, "query_count": len(results),
                "outcomes": dict(Counter(r["status"] for r in results)),
                "errors": deepcopy(adapter.errors)},
        "policy": {"lookback_days": lookback_days, "sample_limit": sample_limit,
                   "history_interval": "[incident_start-lookback, incident_start); whole records only",
                   "activity_match": "directed src/dst + protocol + src_site; not anomaly recurrence"},
        "capabilities": {
            "domain_input": "supplemental_context_only; full domain inventory absent from v3",
            "registration_input": "supplemental_context_only; company is only a supplied label",
            "location_input": "v3 destination country label only",
            "aws": "not_connected"},
        "limitations": [
            "Seen before does not establish benign activity or compromise.",
            "Negative results apply only to declared complete history and the exact criteria/window.",
            "Counts are matched records, not independent connections; incomplete counts are lower bounds.",
            "Attribute prevalence does not establish that the same endpoint or behavior occurred.",
            "IP prevalence is dataset-wide; private IP reuse, NAT and DHCP require scoped interpretation.",
            "V3 omits domains, related-only indicators and full registration attributes.",
            "Current input hypotheses are untrusted context and do not drive queries.",
        ], "results": results}


def escape(value):
    result = html.escape(str(value), quote=True)
    return re.sub(r"([\\`*_{}\[\]()#+.!|>~\-])", r"\\\1", result).replace("\n", " ").replace("\r", " ")


def render_report(result):
    lines = ["# Historical enrichment", "", f"Status: **{result['run']['status']}**",
             f"Adapter: {escape(result['source']['adapter'])}",
             f"Dataset: {escape(result['source'].get('dataset_id', 'not configured'))}",
             f"Synthetic history: {result['source'].get('synthetic', 'not configured')}",
             f"Lookback: {result['policy']['lookback_days']} days before each incident start",
             f"Queries: {result['run']['query_count']}", "",
             "These results describe historical presence, not a compromise verdict.", "",
             "| Incident | Kind | Criteria | Outcome | Records | Complete search | First / last match (UTC) |",
             "|---|---|---|---|---:|---|---|"]
    for row in result["results"]:
        criteria = escape(json.dumps(row["criteria"], sort_keys=True, ensure_ascii=True))
        count = row["matched_record_count"]
        lines.append(f"| {escape(row['incident_id'])} | {escape(row['kind'])} | {criteria} | {escape(row['status'])} | "
                     f"{count if count is not None else 'unknown'} | {row['search_complete']} | "
                     f"{escape(row['first_seen'] or 'unknown')} / {escape(row['last_seen'] or 'unknown')} |")
    lines.extend(["", "## Limitations", ""] + ["- " + escape(x) for x in result["limitations"]])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--history", type=Path, help="Local historical-netflow/1 fixture or subset")
    source.add_argument("--aws-pending", action="store_true", help="Explicit not-configured outcomes; no network")
    parser.add_argument("--context", type=Path)
    parser.add_argument("--lookback-days", type=int, default=30)
    parser.add_argument("--sample-limit", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        handoff, input_hash = load(args.input)
        context, context_hash = load(args.context) if args.context else (None, None)
        adapter = LocalHistory(*load(args.history, 50_000_000)) if args.history else UnconfiguredAWSHistory()
        result = enrich(handoff, adapter, context=context, lookback_days=args.lookback_days,
                        sample_limit=args.sample_limit, handoff_sha256=input_hash,
                        context_sha256=context_hash)
        # Refuse output/input collisions and accidental overwrite of prior evidence.
        targets = [args.output_dir / name for name in ("enrichment_results.json", "enrichment_report.md")]
        inputs = {p.resolve() for p in (args.input, args.history, args.context) if p}
        require(all(p.resolve() not in inputs and not p.exists() for p in targets), "output_already_exists")
        args.output_dir.mkdir(parents=True, exist_ok=True)
        contents = [json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False) + "\n", render_report(result)]
        for path, content in zip(targets, contents):
            with path.open("x", encoding="utf-8") as stream:
                stream.write(content)
        print(f"{result['run']['status']}: {len(result['results'])} historical queries")
        return 0 if result["run"]["status"] == "completed" else 2
    except ContractError as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 1
    except OSError:
        print("File access failed; check input paths and output permissions.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
