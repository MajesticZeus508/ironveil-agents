"""Single-attempt managed writes with bounded, secret-free diagnostics.

Agent-owned copies live in each pod; keep their parity regression passing.
Never serialize exception messages, causes, response bodies, URLs or headers.
"""
import os


def error_class(exc):
    name = type(exc).__name__
    return name if name in {
        "ValueError", "TypeError", "RuntimeError", "TimeoutError", "UnicodeEncodeError",
        "ConnectTimeout", "ReadTimeout", "WriteTimeout", "PoolTimeout", "ConnectError",
        "ReadError", "WriteError", "RemoteProtocolError", "HTTPStatusError", "SSLError",
    } else "OtherError"


def diagnostic(category, *, status=None, exc=None, sent=None):
    return {"operation": "managed_file_write", "category": category,
            "http_status": status, "exception_type": error_class(exc) if exc is not None else None,
            "request_may_have_been_sent": sent, "retry_policy": "never_automatically_retry"}


def sanitize_diagnostic(value):
    """Allowlisted projection for an orchestrator reading remote tool content."""
    allowed = {"missing_sgp_configuration", "invalid_sgp_configuration", "write_exception",
               "authentication_rejected", "permission_denied", "rate_limited", "storage_unavailable",
               "http_rejected", "invalid_success_response", "request_not_sent",
               "transport_or_client_failure", "invalid_write_response"}
    category = value.get("category")
    category = category if type(category) is str and category in allowed else "invalid_write_response"
    status, sent, name = value.get("http_status"), value.get("request_may_have_been_sent"), value.get("exception_type")
    result = diagnostic(category, status=status if type(status) is int and 100 <= status <= 599 else None,
                        sent=sent if type(sent) is bool else None)
    allowed_names = {"ValueError", "TypeError", "RuntimeError", "TimeoutError", "UnicodeEncodeError",
                     "ConnectTimeout", "ReadTimeout", "WriteTimeout", "PoolTimeout", "ConnectError",
                     "ReadError", "WriteError", "RemoteProtocolError", "HTTPStatusError", "SSLError", "OtherError"}
    result["exception_type"] = name if type(name) is str and name in allowed_names else None
    return result


async def write_once(store, filename, content, mime_type):
    """Return (confirmed ID or None, safe diagnostic or None). Never retry.

    Only the actual SDK client's URL resolution is preflighted; no guessed
    host, fallback, credential or mutation. A null sent flag means unknown.
    """
    try:
        from spark_agent_kit.middleware.resources.sgp_client import SGPResourceClient
    except ImportError:
        SGPResourceClient = ()  # Dependency-free unit-test stores.
    if isinstance(store, SGPResourceClient):
        try:
            store.base_url  # Public SDK property; resolves without network I/O.
        except ValueError as exc:
            category = "invalid_sgp_configuration" if os.getenv("SGP_API_URL", "").strip() else "missing_sgp_configuration"
            return None, diagnostic(category, exc=exc, sent=False)
    try:
        response = await store.write_file(filename, content, mime_type=mime_type)
    except Exception as exc:
        # No generic exception proves whether dispatch began. Cancellation
        # (BaseException) deliberately propagates instead of becoming a result.
        return None, diagnostic("write_exception", exc=exc)
    status = getattr(response, "status", None)
    status = status if type(status) is int and 100 <= status <= 599 else None
    body = getattr(response, "body", None)
    failed = getattr(response, "ok", None) is False
    if not failed and status is not None and 200 <= status < 300 and isinstance(body, dict):
        file_id = body.get("id")
        if (type(file_id) is str and file_id.strip() and len(file_id) <= 256
                and not any(ord(c) < 32 for c in file_id)):
            return file_id, None
    sent = getattr(response, "request_may_have_been_sent", None)
    sent = sent if type(sent) is bool else None
    cause = getattr(response, "cause", None)
    if status is not None:
        # A real HTTP response proves dispatch, even if a supplied flag disagrees.
        sent = True
        category = ("authentication_rejected" if status == 401 else
                    "permission_denied" if status == 403 else
                    "rate_limited" if status == 429 else
                    "storage_unavailable" if status >= 500 else
                    "http_rejected" if not 200 <= status < 300 else
                    "invalid_success_response")
    else:
        category = "request_not_sent" if sent is False else "transport_or_client_failure" if failed else "invalid_write_response"
    return None, diagnostic(category, status=status, exc=cause if isinstance(cause, Exception) else None, sent=sent)
