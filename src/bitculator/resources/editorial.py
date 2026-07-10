from __future__ import annotations

from typing import Any, Union

from ..pagination import Page
from ._base import Resource


class EditorialResource(Resource):
    """Editorial content: articles, videos, and insights."""

    def coin_videos(self, slug: str, **params: Any) -> Page:
        """Videos for a coin (paginated). Params: page, per_page, type, search."""
        return self._http.get_page(f"/api/v1/coins/{self._enc(slug)}/videos", params)

    def coin_insights(self, slug: str, **params: Any) -> Any:
        """Insight timeline for a coin. Params: locale, offset, limit."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/insights", params)

    def articles(self, **params: Any) -> Page:
        """List articles (paginated). Params: page, per_page, locale, tag, coin,
        exchange, wallet, search."""
        return self._http.get_page("/api/v1/articles", params)

    def article(self, slug: str, **params: Any) -> Any:
        """Get a single article by slug. Params: locale."""
        return self._http.get(f"/api/v1/articles/{self._enc(slug)}", params)

    def submit_article_feedback(self, slug: str, *, helpful: bool) -> Any:
        """Submit helpful/unhelpful feedback on an article."""
        return self._http.post(f"/api/v1/articles/{self._enc(slug)}/feedback", {"helpful": helpful})

    def video(self, id: Union[str, int]) -> Any:
        """Get a single video by id."""
        return self._http.get(f"/api/v1/videos/{self._enc(id)}")

    def insights(self, **params: Any) -> Page:
        """List insights (paginated). Params: page, per_page, locale, type, coin, search, sort."""
        return self._http.get_page("/api/v1/insights", params)

    def insight(self, id: Union[str, int], **params: Any) -> Any:
        """Get a single insight by id. Params: locale."""
        return self._http.get(f"/api/v1/insights/{self._enc(id)}", params)
