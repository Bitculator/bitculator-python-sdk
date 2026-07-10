from __future__ import annotations

from typing import Any

from ..pagination import Page
from ._base import Resource


class GlobalMarketResource(Resource):
    """Global market aggregates."""

    def snapshot(self) -> Any:
        """Global market snapshot (total marketcap, volume, dominance, ...)."""
        return self._http.get("/api/v1/global")

    def heatmap(self) -> Any:
        """Market heatmap data."""
        return self._http.get("/api/v1/global/heatmap")

    def history(self, metric: str, **params: Any) -> Any:
        """Global marketcap or volume history. ``metric`` is e.g. ``marketcap`` or ``volume``. Params: period."""
        return self._http.get(f"/api/v1/global/history/{self._enc(metric)}", params)


class SentimentResource(Resource):
    """Community sentiment and market-wide sentiment indices."""

    def votes(self, slug: str) -> Any:
        """Community vote tallies for a coin."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/votes")

    def vote(self, slug: str, *, vote: str) -> Any:
        """Cast a sentiment vote for a coin (``bullish`` or ``bearish``)."""
        return self._http.post(f"/api/v1/coins/{self._enc(slug)}/votes", {"vote": vote})

    def fear_greed(self, **params: Any) -> Any:
        """Fear & Greed index. Params: coin."""
        return self._http.get("/api/v1/sentiment/fear-greed", params)

    def bull_bear(self, **params: Any) -> Any:
        """Bull / Bear index. Params: coin."""
        return self._http.get("/api/v1/sentiment/bull-bear", params)

    def altseason(self, **params: Any) -> Any:
        """Altseason index. Params: days."""
        return self._http.get("/api/v1/sentiment/altseason", params)

    def indicators(self) -> Any:
        """Aggregate market indicator tally."""
        return self._http.get("/api/v1/sentiment/indicators")


class LiquidationsResource(Resource):
    """Liquidation feed and aggregates."""

    def feed(self, **params: Any) -> Page:
        """Live liquidation feed (paginated). Params: page, per_page, exchange,
        instrument, position, order, symbol, min_usd."""
        return self._http.get_page("/api/v1/liquidations", params)

    def hourly(self, **params: Any) -> Any:
        """Hourly liquidation totals. Params: hours."""
        return self._http.get("/api/v1/liquidations/hourly", params)

    def daily(self, **params: Any) -> Any:
        """Daily liquidation totals. Params: days."""
        return self._http.get("/api/v1/liquidations/daily", params)

    def summary(self) -> Any:
        """Today's liquidation summary."""
        return self._http.get("/api/v1/liquidations/summary")

    def netflow(self, **params: Any) -> Any:
        """Long/short liquidation netflow. Params: days."""
        return self._http.get("/api/v1/liquidations/netflow", params)

    def coins(self, **params: Any) -> Any:
        """Most-liquidated coins. Params: hours, limit."""
        return self._http.get("/api/v1/liquidations/coins", params)
