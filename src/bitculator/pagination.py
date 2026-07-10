"""
A single page of a paginated list, plus lazy forward navigation.

``page.data`` is the current page's rows. Iterating a ``Page`` (or calling
``auto_paging_iter()``) transparently walks every following page.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ._http import HttpClient


class Page:
    def __init__(self, http: HttpClient, path: str, params: dict, envelope: Any) -> None:
        env = envelope if isinstance(envelope, dict) else {}
        #: Rows on this page.
        self.data: list[Any] = env.get("data", []) or []
        #: Laravel paginator metadata (current_page, last_page, total, ...).
        self.meta: dict = env.get("meta", {}) or {}
        #: Page navigation links.
        self.links: dict = env.get("links", {}) or {}
        self._http = http
        self._path = path
        self._params = params

    @property
    def has_more(self) -> bool:
        """True if at least one more page exists."""
        if self.links.get("next"):
            return True
        current, last = self.meta.get("current_page"), self.meta.get("last_page")
        return current is not None and last is not None and current < last

    def next_page(self) -> Page | None:
        """Fetch the next page, or ``None`` if this is the last one."""
        if not self.has_more:
            return None
        next_number = (self.meta.get("current_page") or 1) + 1
        return self._http.get_page(self._path, {**self._params, "page": next_number})

    def auto_paging_iter(self) -> Iterator[Any]:
        """Yield every row across this and all following pages, fetching lazily."""
        page: Page | None = self
        while page is not None:
            yield from page.data
            page = page.next_page()

    def __iter__(self) -> Iterator[Any]:
        """Iterating a page walks all pages (use ``.data`` for just this page)."""
        return self.auto_paging_iter()

    def __len__(self) -> int:
        return len(self.data)

    def __repr__(self) -> str:
        return f"<Page rows={len(self.data)} page={self.meta.get('current_page')}/{self.meta.get('last_page')}>"
