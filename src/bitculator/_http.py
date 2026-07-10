"""
The DRY transport core. Every request in the SDK flows through
``HttpClient._request``: URL + query building, auth headers, JSON
(de)serialization, the response envelope, quota capture, retries with backoff,
timeouts, and error mapping all live here — nowhere else. Uses only the standard
library (``urllib``) so the SDK has zero runtime dependencies.
"""

from __future__ import annotations

import decimal
import http.client
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Optional

from .errors import APIConnectionError, APIDecodeError, APIError, APITimeoutError, BitculatorError
from .pagination import Page


@dataclass
class Quota:
    """Quota headers (``X-Quota-*``) from the most recent response."""

    limit: Optional[int]
    remaining: Optional[int]
    reset: Optional[int]
    raw: dict


class HttpClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float,
        max_retries: int,
        user_agent: str,
        on_quota: Callable[[Quota], None],
        opener: Optional[urllib.request.OpenerDirector] = None,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._user_agent = user_agent
        self._on_quota = on_quota
        self._opener = opener or urllib.request.build_opener()

    def get(self, path: str, params: Optional[dict] = None) -> Any:
        return _unwrap(self._request("GET", path, params=params))

    def post(self, path: str, body: Any = None, params: Optional[dict] = None) -> Any:
        return _unwrap(self._request("POST", path, params=params, body=body))

    def delete(self, path: str, params: Optional[dict] = None) -> Any:
        return _unwrap(self._request("DELETE", path, params=params))

    def get_page(self, path: str, params: Optional[dict] = None) -> Page:
        envelope = self._request("GET", path, params=params)
        return Page(self, path, params or {}, envelope)

    def _request(self, method: str, path: str, params: Optional[dict] = None, body: Any = None) -> Any:
        url = self._base_url + path + _query(params)
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
            "User-Agent": self._user_agent,
        }
        data: Optional[bytes] = None
        if body is not None:
            try:
                data = json.dumps(_snake_keys(body)).encode("utf-8")
            except (TypeError, ValueError) as exc:
                raise BitculatorError(f"Failed to encode request body: {exc}") from exc
            headers["Content-Type"] = "application/json"

        # Idempotency gate: GET/DELETE are safe to auto-retry; POST is NOT, so a
        # POST the server may already have processed is never re-sent on a 5xx or
        # a network/timeout error. A 429 means the server rejected it before
        # processing, so it stays retryable for every method.
        is_idempotent = method in ("GET", "DELETE")

        attempt = 0
        while True:
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with self._opener.open(request, timeout=self._timeout) as response:
                    self._on_quota(_parse_quota(response.headers))
                    raw = response.read()
                    if not raw:
                        return None
                    try:
                        return json.loads(raw)
                    except (ValueError, TypeError) as exc:
                        raise APIDecodeError(f"Failed to decode response from {path}: {exc}") from exc
            except urllib.error.HTTPError as exc:
                self._on_quota(_parse_quota(exc.headers))
                raw = exc.read()
                payload = _safe_json(raw)
                status = exc.code
                retryable = status == 429 or (status >= 500 and is_idempotent)
                if retryable and attempt < self._max_retries:
                    time.sleep(_retry_delay(exc.headers, attempt))
                    attempt += 1
                    continue
                raise APIError.from_response(status, payload, exc.headers) from None
            except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as exc:
                if is_idempotent and attempt < self._max_retries:
                    time.sleep(_backoff(attempt))
                    attempt += 1
                    continue
                reason = getattr(exc, "reason", exc)
                if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
                    raise APITimeoutError(f"Request to {path} timed out after {self._timeout}s") from exc
                raise APIConnectionError(f"Network error requesting {path}: {reason}") from exc


# ── helpers (all pure; the single place these concerns are implemented) ──────


def _unwrap(envelope: Any) -> Any:
    """Unwrap the ``{"data": ...}`` envelope; pass through bodies with no data key."""
    if isinstance(envelope, dict) and "data" in envelope:
        return envelope["data"]
    return envelope


def _query(params: Optional[dict]) -> str:
    """Serialize params: drop ``None``, lists→CSV, bools→true/false, trailing ``_`` stripped (``from_``→``from``)."""
    if not params:
        return ""
    pairs = []
    for key, value in params.items():
        if value is None:
            continue
        name = key[:-1] if key.endswith("_") else key
        if isinstance(value, (list, tuple)):
            if not value:
                continue
            pairs.append((name, ",".join(str(item) for item in value)))
        elif isinstance(value, bool):
            pairs.append((name, "true" if value else "false"))
        elif isinstance(value, float):
            # Plain-decimal form (0.0000001, not 1e-07) — keeps the wire format
            # identical across the SDK family.
            pairs.append((name, format(decimal.Decimal(repr(value)), "f")))
        else:
            pairs.append((name, str(value)))
    return "?" + urllib.parse.urlencode(pairs) if pairs else ""


def _snake_keys(body: Any) -> Any:
    """Strip a trailing underscore from body keys (``from_``→``from``); leave the rest as-is."""
    if not isinstance(body, dict):
        return body
    return {(key[:-1] if key.endswith("_") else key): value for key, value in body.items()}


def _parse_quota(headers: Any) -> Quota:
    raw = {}
    if headers is not None:
        for key, value in headers.items():
            lowered = key.lower()
            if lowered.startswith("x-quota-"):
                raw[lowered] = value

    def num(name: str) -> Optional[int]:
        value = raw.get(name)
        if value in (None, ""):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    return Quota(
        limit=num("x-quota-limit"),
        remaining=num("x-quota-remaining"),
        reset=num("x-quota-reset"),
        raw=raw,
    )


def _retry_delay(headers: Any, attempt: int) -> float:
    retry_after = headers.get("retry-after") if headers is not None else None
    try:
        seconds = int(retry_after)
        if seconds > 0:
            # Cap at 60s: a misbehaving proxy must not block a synchronous call for an hour.
            return float(min(seconds, 60))
    except (TypeError, ValueError):
        pass
    return _backoff(attempt)


def _backoff(attempt: int) -> float:
    """Exponential backoff with jitter, capped at 8s."""
    return min(8.0, 0.25 * (2 ** attempt)) + random.uniform(0.0, 0.1)


def _safe_json(raw: bytes) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except (ValueError, TypeError):
        return None
