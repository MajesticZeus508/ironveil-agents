"""Verified current-run Enrichment JSON -> Recommendation; no new lookup source."""
import hashlib
import json

if __package__:
    from .handoff import invoke_enrichment
    from .structured_handoff import prepare_handoff, verify_structured_receipt
else:
    from handoff import invoke_enrichment
    from structured_handoff import prepare_handoff, verify_structured_receipt


async def recommend_from_enrichment(child, store, *, correlation=None, invoke=None):
    skipped = {"platform_status": "not_invoked", "application_status": "unknown", "exports": [],
               "error": "enrichment_json_unavailable_or_unverified"}
    if child.get("platform_status") != "completed" or child.get("error"):
        return skipped
    if child.get("input_mode") == "structured" or "structured_result" in child:
        try:
            envelope = child["structured_result"]
            if (envelope.get("status") != "ready" or envelope.get("schema") != "alert-enrichment/1"
                    or envelope.get("canonicalization") != "canonical-json/1"):
                return skipped
            prepared = prepare_handoff(envelope["payload"], recommendation=True)
            if (prepared["payload_sha256"] != envelope.get("payload_sha256")
                    or prepared["handoff"].get("handoff_receipt") != child.get("handoff_receipt")):
                return skipped
            verify_structured_receipt(child["handoff_receipt"], child)
        except (ValueError, TypeError, KeyError):
            return skipped
        return await (invoke or invoke_enrichment)(prepared, correlation=correlation, recommendation=True)
    candidates = [item for item in child.get("exports", [])
                  if item.get("filename") == "enrichment_results.json"
                  and item.get("mime_type") == "application/json" and item.get("status") == "created"]
    if len(candidates) != 1:
        return skipped
    export = dict(candidates[0])
    try:
        response = await store.read_file_bytes(export["file_id"], max_bytes=20_000_000)
        if type(response.status) is not int or not 200 <= response.status < 300 or not isinstance(response.body, bytes):
            return skipped
        data = json.loads(response.body)
        receipt = data.get("handoff_receipt", {})
        if (data.get("schema") != "alert-enrichment/1" or receipt != child.get("handoff_receipt")
                or receipt.get("file_id") != child.get("file_id")
                or receipt.get("sha256") != child.get("sha256")):
            return skipped
        if child.get("input_mode") == "structured":
            verify_structured_receipt(receipt, child)
        export["sha256"] = hashlib.sha256(response.body).hexdigest()
    except Exception:
        return skipped
    try:
        return await (invoke or invoke_enrichment)(export, correlation=correlation, recommendation=True)
    except Exception:
        return {"platform_status": "unknown", "application_status": "unknown", "exports": [],
                "error": "recommendation_failed_or_uncertain"}
