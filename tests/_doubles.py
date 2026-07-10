"""
Test doubles for the transport seam. The SDK takes any
``urllib.request.OpenerDirector``-compatible object via ``opener=``, so tests
inject one that serves queued canned responses and records every request —
no network, no mocking framework.
"""

from __future__ import annotations

import io
import json
import urllib.error
from dataclasses import dataclass, field
from email.message import Message
from typing import Any, List, Optional


def make_headers(pairs: Optional[dict] = None) -> Message:
    """Build the case-insensitive header mapping urllib itself uses."""
    message = Message()
    for key, value in (pairs or {}).items():
        message[key] = value
    return message


@dataclass
class RecordedCall:
    url: str
    method: str
    headers: dict
    body: Optional[bytes]
    timeout: Optional[float]

    def header(self, name: str) -> Optional[str]:
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return None


class FakeResponse:
    """A 2xx response: context manager with ``headers`` and ``read()``."""

    def __init__(self, body: bytes, headers: Optional[dict] = None) -> None:
        self._body = body
        self.headers = make_headers(headers)

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc_info: Any) -> None:
        return None


def ok(body: Any = None, headers: Optional[dict] = None) -> FakeResponse:
    raw = b"" if body is None else json.dumps(body).encode("utf-8")
    return FakeResponse(raw, headers)


def raw_response(text: str, headers: Optional[dict] = None) -> FakeResponse:
    return FakeResponse(text.encode("utf-8"), headers)


def http_error(status: int, body: Any = None, headers: Optional[dict] = None) -> urllib.error.HTTPError:
    raw = b"" if body is None else json.dumps(body).encode("utf-8")
    return urllib.error.HTTPError("https://api.test", status, f"HTTP {status}", make_headers(headers), io.BytesIO(raw))


def raw_http_error(status: int, text: str, headers: Optional[dict] = None) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://api.test", status, f"HTTP {status}", make_headers(headers), io.BytesIO(text.encode("utf-8")))


@dataclass
class FakeOpener:
    """Shifts one queued step per ``open()`` call: a FakeResponse to return or an Exception to raise."""

    steps: List[Any] = field(default_factory=list)
    calls: List[RecordedCall] = field(default_factory=list)

    def open(self, request: Any, timeout: Optional[float] = None) -> FakeResponse:
        self.calls.append(
            RecordedCall(
                url=request.full_url,
                method=request.get_method(),
                headers=dict(request.header_items()),
                body=request.data,
                timeout=timeout,
            )
        )
        if not self.steps:
            raise AssertionError("FakeOpener: no more queued responses")
        step = self.steps.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def make_client(*steps: Any, **overrides: Any):
    """A Bitculator client wired to a FakeOpener, with test-friendly defaults."""
    from bitculator import Bitculator

    opener = FakeOpener(list(steps))
    defaults = {"base_url": "https://api.test", "timeout": 2.0, "max_retries": 2, "user_agent": "bitculator-python/test"}
    defaults.update(overrides)
    client = Bitculator("test-key", opener=opener, **defaults)
    return client, opener
