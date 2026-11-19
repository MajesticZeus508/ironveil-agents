"""Bounded, explicit LUX payload serialization; no network or free-text parsing."""
import json

MAX_EVENT_BYTES = 1_000_000


def serialize_event(event):
    """Hash/parse this documented serialization, NOT original transport bytes."""
    if not isinstance(event, dict):
        raise ValueError("LUX event payload must be a finding object.")
    try:
        content = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        size = len(content.encode("utf-8"))
    except (ValueError, TypeError, RecursionError, UnicodeError):
        raise ValueError("LUX event must contain finite, UTF-8 JSON data.") from None
    if size > MAX_EVENT_BYTES:
        raise ValueError("LUX event exceeds 1,000,000 serialized UTF-8 bytes; refused, not truncated.")
    return content
