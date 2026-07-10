from __future__ import annotations

import urllib.parse
from typing import Any

from .._http import HttpClient


class Resource:
    """Shared base for every resource group: holds the transport and encodes path segments."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http

    @staticmethod
    def _enc(value: Any) -> str:
        """Percent-encode a dynamic path segment (slug or id) so it is URL-safe."""
        return urllib.parse.quote(str(value), safe="")
