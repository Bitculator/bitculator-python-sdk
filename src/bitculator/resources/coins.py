from __future__ import annotations

from typing import Any

from ..pagination import Page
from ._base import Resource


class CoinsResource(Resource):
    """Coins & tokens: listings, movers, detail, and history."""

    def list(self, **params: Any) -> Page:
        """List coins (paginated). Params: page, per_page, type, status, search,
        min_price, max_price, min_marketcap, max_marketcap, min_volume, max_volume,
        ids, slugs, symbols, sort, interval."""
        return self._http.get_page("/api/v1/coins", params)

    def recently_added(self, **params: Any) -> Page:
        """Recently added coins (paginated). Same params as :meth:`list`."""
        return self._http.get_page("/api/v1/coins/recently-added", params)

    def gainers(self, **params: Any) -> Page:
        """Top gainers (paginated). Same params as :meth:`list`."""
        return self._http.get_page("/api/v1/coins/gainers", params)

    def losers(self, **params: Any) -> Page:
        """Top losers (paginated). Same params as :meth:`list`."""
        return self._http.get_page("/api/v1/coins/losers", params)

    def trending(self, **params: Any) -> Any:
        """Trending coins. Params: limit."""
        return self._http.get("/api/v1/coins/trending", params)

    def get(self, slug: str, **params: Any) -> Any:
        """Get a single coin by slug. Params: locale."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}", params)

    def history(self, slug: str, **params: Any) -> Any:
        """OHLC candle history. Params: interval, start, end, limit."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/history", params)

    def marketcap_history(self, slug: str, **params: Any) -> Any:
        """Marketcap history. Params: interval, start, end, limit."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/marketcap-history", params)

    def sparkline(self, slug: str, **params: Any) -> Any:
        """Price sparkline. Params: period."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/sparkline", params)


class PricesResource(Resource):
    """Lightweight price lookups."""

    def list(self, **params: Any) -> Any:
        """Get prices for many coins at once. Params: ids, slugs, symbols, convert."""
        return self._http.get("/api/v1/prices", params)

    def get(self, slug: str, **params: Any) -> Any:
        """Get the price of a single coin. Params: convert."""
        return self._http.get(f"/api/v1/prices/{self._enc(slug)}", params)

    def historical(self, **params: Any) -> Any:
        """Historical price of a coin on a date. Params: slug, date."""
        return self._http.get("/api/v1/historical-price", params)


class ConversionResource(Resource):
    """Asset conversion and reference rates."""

    def convert(self, **params: Any) -> Any:
        """Convert an amount between two assets. Params: from_ (-> ``from``), to, amount."""
        return self._http.get("/api/v1/convert", params)

    def fiats(self) -> Any:
        """List supported fiat currencies."""
        return self._http.get("/api/v1/fiats")

    def rates(self) -> Any:
        """List conversion rates."""
        return self._http.get("/api/v1/rates")
