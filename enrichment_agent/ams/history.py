"""History adapter boundary. No AWS dependency or network access in this build."""
from typing import Any, Protocol, cast

if __package__:
    from .contracts import (ContractError, OPTIONAL, integer, ip, require,
                            text, timestamp, window)
else:
    from contracts import (ContractError, OPTIONAL, integer, ip, require,
                           text, timestamp, window)

FIELDS = {"src": ip, "dst": ip, "protocol": lambda x: text(x).upper(),
          "src_site": text, "dst_country": text, "dst_company": text,
          "bytes_sent": integer, "bytes_received": integer, **OPTIONAL}


class HistoryAdapter(Protocol):
    metadata: dict
    errors: list

    def search(self, criteria: dict, start, end, sample_limit: int) -> dict: ...


class UnconfiguredAWSHistory:
    metadata = {"adapter": "aws_not_configured", "status": "not_configured"}
    errors = []

    def search(self, criteria, start, end, sample_limit):
        return {"status": "not_configured", "search_complete": False,
                "matched_record_count": None, "first_seen": None, "last_seen": None,
                "samples": [], "samples_truncated": False}


class LocalHistory:
    def __init__(self, data: Any, sha256):
        require(isinstance(data, dict) and data.get("schema") == "historical-netflow/1", "unsupported_history")
        text(data.get("dataset_id"))
        require(type(data.get("synthetic")) is bool, "synthetic_flag_required")
        self.start, self.end = window(data.get("coverage"))
        require(type(data["coverage"].get("complete")) is bool, "coverage_completeness_required")
        fields = data.get("fields")
        require(isinstance(fields, list) and all(isinstance(x, str) for x in fields), "invalid_fields")
        fields = cast(list[str], fields)
        require(len(set(fields)) == len(fields) and {"src", "dst"} <= set(fields) <= FIELDS.keys(), "invalid_fields")
        self.fields = set(fields)
        self.metadata = {"adapter": "local_history", "dataset_id": data["dataset_id"],
                         "sha256": sha256, "synthetic": data["synthetic"],
                         "coverage": data["coverage"], "fields": fields}
        rows = data.get("records")
        require(isinstance(rows, list) and len(rows) <= 100_000, "history_record_limit")
        rows = cast(list, rows)
        self.errors, records, quarantined = [], {}, set()
        self.duplicates = 0
        for index, row in enumerate(rows, 1):
            key = row.get("record_id") if isinstance(row, dict) else None
            try:
                require(isinstance(row, dict), "invalid_history_record")
                text(key)
                require(set(row) == {"record_id", "start", "end", *fields}, "history_field_mismatch")
                start, end = window(row)
                require(self.start <= start <= end <= self.end, "record_outside_coverage")
                normalized = {k: FIELDS[k](row[k]) for k in fields}
                normalized.update(record_id=key, start=start.isoformat(), end=end.isoformat())
                if key in quarantined:
                    continue
                if key in records:
                    require(records[key][0] == normalized, "conflicting_record_id")
                    self.duplicates += 1
                else:
                    records[key] = (normalized, index)
            except ContractError as exc:
                self.errors.append({"record_index": index, "code": str(exc)})
                if isinstance(key, str):
                    records.pop(key, None)
                    quarantined.add(key)
        self.records = sorted(records.values(), key=lambda x: (x[0]["start"], x[0]["record_id"]))
        self.metadata.update(valid_records=len(self.records), duplicates_collapsed=self.duplicates,
                             validation_errors=self.errors)

    def search(self, criteria, start, end, sample_limit):
        needed = {"src", "dst"} if "endpoint_ip" in criteria else set(criteria)
        if not needed <= self.fields:
            return {"status": "unsupported", "search_complete": False,
                    "missing_fields": sorted(needed - self.fields), "matched_record_count": None,
                    "first_seen": None, "last_seen": None, "samples": [], "samples_truncated": False}
        complete = (self.metadata["coverage"]["complete"] and not self.errors
                    and self.start <= start and self.end >= end)
        matches = []
        for row, index in self.records:
            rs, re = timestamp(row["start"]), timestamp(row["end"])
            if not (start <= rs < end and re <= end):
                continue
            match = (criteria["endpoint_ip"] in (row["src"], row["dst"]) if "endpoint_ip" in criteria
                     else all(row[k] == value for k, value in criteria.items()))
            if match:
                matches.append((row, index))
        return {"status": "seen" if matches else ("no_match_in_covered_history" if complete else "unknown"),
                "search_complete": complete, "matched_record_count": len(matches),
                "first_seen": min((r["start"] for r, _ in matches), key=timestamp, default=None),
                "last_seen": max((r["end"] for r, _ in matches), key=timestamp, default=None),
                "samples": [{"record_id": r["record_id"], "record_index": i,
                             "start": r["start"], "end": r["end"]} for r, i in matches[:sample_limit]],
                "samples_truncated": len(matches) > sample_limit}
