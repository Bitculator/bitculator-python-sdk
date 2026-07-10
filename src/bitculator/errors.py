"""
Exception hierarchy. Everything the SDK raises derives from ``BitculatorError``,
so a single ``except BitculatorError`` covers it all. HTTP failures raise a
status-specific ``APIError`` subclass carrying the API's
``{"error": {"code", "message", "details"}}`` envelope.

(Note: 403 is ``PermissionDeniedError`` and timeouts are ``APITimeoutError`` to
avoid shadowing the built-in ``PermissionError`` / ``TimeoutError``.)
"""

from __future__ import annotations

from typing import Any


class BitculatorError(Exception):
    """Base class for every error raised by the SDK."""


class APITimeoutError(BitculatorError):
    """The request exceeded the configured timeout (after retries)."""


class APIConnectionError(BitculatorError):
    """A network-level failure prevented the request from completing."""


class APIDecodeError(BitculatorError):
    """A 2xx body could not be parsed."""


class APIError(BitculatorError):
    """A non-2xx response. Subclasses map to specific status codes."""

    def __init__(self, status: int, body: dict | None, request_id: str | None) -> None:
        err = body or {}
        self.status = status
        self.code: str | None = err.get("code")
        self.details: Any = err.get("details")
        self.request_id = request_id
        self.message: str = err.get("message") or f"HTTP {status}"
        super().__init__(self.message)

    @staticmethod
    def from_response(status: int, json_body: Any, headers: Any) -> APIError:
        """Build the most specific error subclass for a failed response."""
        body = _error_body(json_body)
        request_id = headers.get("x-request-id") if headers is not None else None
        if status == 429:
            return RateLimitError(status, body, request_id, _to_int(_header(headers, "retry-after")))
        cls = _STATUS_MAP.get(status)
        if cls is not None:
            return cls(status, body, request_id)
        if status >= 500:
            return ServerError(status, body, request_id)
        return APIError(status, body, request_id)


class AuthenticationError(APIError):
    """401 — missing, malformed, or invalid API key."""


class PermissionDeniedError(APIError):
    """403 — the key's plan does not grant access to this endpoint."""


class NotFoundError(APIError):
    """404 — the requested resource does not exist."""


class ValidationError(APIError):
    """422 — invalid parameters (see ``details``)."""


class ServerError(APIError):
    """5xx — an error on the API side."""


class RateLimitError(APIError):
    """429 — quota or rate limit exceeded."""

    def __init__(
        self,
        status: int,
        body: dict | None,
        request_id: str | None,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(status, body, request_id)
        self.retry_after = retry_after


_STATUS_MAP = {
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: ValidationError,
}


def _error_body(json_body: Any) -> dict | None:
    if isinstance(json_body, dict):
        err = json_body.get("error")
        if isinstance(err, dict):
            return err
        if isinstance(json_body.get("message"), str):
            return {"message": json_body["message"]}
    return None


def _header(headers: Any, name: str) -> Any:
    return headers.get(name) if headers is not None else None


def _to_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
