from __future__ import annotations

from typing import Any, Union

from ..pagination import Page
from ._base import Resource


class MarketsResource(Resource):
    """Markets, tickers, and trading pairs."""

    def coin_markets(self, slug: str, **params: Any) -> Page:
        """Markets (tickers) for a coin (paginated). Params: page, per_page, exchange,
        pair, instrument, search, min_volume, max_volume, min_change, max_change, sort."""
        return self._http.get_page(f"/api/v1/coins/{self._enc(slug)}/markets", params)

    def coin_symbols(self, slug: str) -> Any:
        """Trading symbols for a coin."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/symbols")

    def tickers(self, **params: Any) -> Page:
        """List tickers across the market (paginated). Same params as :meth:`coin_markets`."""
        return self._http.get_page("/api/v1/tickers", params)

    def pairs(self, **params: Any) -> Page:
        """List trading pairs (paginated). Params: page, per_page, search, coin,
        min_volume, max_volume, sort."""
        return self._http.get_page("/api/v1/pairs", params)

    def pair(self, id: Union[str, int]) -> Any:
        """Get a single trading pair by id."""
        return self._http.get(f"/api/v1/pairs/{self._enc(id)}")


class ExchangesResource(Resource):
    """Exchanges: listings, trust score, history, markets, and listed assets."""

    def list(self, **params: Any) -> Page:
        """List exchanges (paginated). Params: page, per_page, type, search, min_pairs,
        max_pairs, min_assets, max_assets, min_volume, max_volume, ids, slugs, sort."""
        return self._http.get_page("/api/v1/exchanges", params)

    def get(self, slug: str) -> Any:
        """Get a single exchange by slug."""
        return self._http.get(f"/api/v1/exchanges/{self._enc(slug)}")

    def trust_score(self, slug: str) -> Any:
        """Get an exchange's trust score."""
        return self._http.get(f"/api/v1/exchanges/{self._enc(slug)}/trust-score")

    def history(self, slug: str, **params: Any) -> Any:
        """Volume/history for an exchange. Params: interval, start, end, limit."""
        return self._http.get(f"/api/v1/exchanges/{self._enc(slug)}/history", params)

    def sparkline(self, slug: str, **params: Any) -> Any:
        """Sparkline for an exchange. Params: period."""
        return self._http.get(f"/api/v1/exchanges/{self._enc(slug)}/sparkline", params)

    def tickers(self, slug: str, **params: Any) -> Page:
        """Markets (tickers) on an exchange (paginated)."""
        return self._http.get_page(f"/api/v1/exchanges/{self._enc(slug)}/tickers", params)

    def assets(self, slug: str, **params: Any) -> Page:
        """Coins listed on an exchange (paginated)."""
        return self._http.get_page(f"/api/v1/exchanges/{self._enc(slug)}/assets", params)


class WalletsResource(Resource):
    """Wallets: listings, release timeline, comparison, and supported coins."""

    def list(self, **params: Any) -> Page:
        """List wallets (paginated). Params: page, per_page, search, min_score,
        max_score, tags, ids, slugs, sort."""
        return self._http.get_page("/api/v1/wallets", params)

    def timeline(self, **params: Any) -> Page:
        """Wallet release timeline (paginated). Same params as :meth:`list`."""
        return self._http.get_page("/api/v1/wallets/timeline", params)

    def compare(self, **params: Any) -> Any:
        """Compare a set of wallets side by side. Params: slugs."""
        return self._http.get("/api/v1/wallets/compare", params)

    def get(self, slug: str) -> Any:
        """Get a single wallet by slug."""
        return self._http.get(f"/api/v1/wallets/{self._enc(slug)}")

    def assets(self, slug: str, **params: Any) -> Page:
        """Coins supported by a wallet (paginated)."""
        return self._http.get_page(f"/api/v1/wallets/{self._enc(slug)}/assets", params)
