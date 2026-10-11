from __future__ import annotations

from typing import Any

from ._base import Resource


class IndicatorsResource(Resource):
    """Technical indicators for a coin.

    Period indicators (rsi, stoch_rsi, sma, cci, mfi, williams_r, price_volatility,
    volume_volatility) accept: period, start, end, limit.
    Series indicators (macd, obv, adx, vwap, cmf) accept: start, end, limit.
    """

    def _indicator(self, slug: str, name: str, params: dict) -> Any:
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/indicators/{name}", params)

    def snapshot(self, slug: str) -> Any:
        """All indicators for a coin at a glance."""
        return self._http.get(f"/api/v1/coins/{self._enc(slug)}/indicators")

    def rsi(self, slug: str, **params: Any) -> Any:
        """Relative Strength Index."""
        return self._indicator(slug, "rsi", params)

    def stoch_rsi(self, slug: str, **params: Any) -> Any:
        """Stochastic RSI."""
        return self._indicator(slug, "stoch-rsi", params)

    def sma(self, slug: str, **params: Any) -> Any:
        """Simple Moving Average."""
        return self._indicator(slug, "sma", params)

    def cci(self, slug: str, **params: Any) -> Any:
        """Commodity Channel Index."""
        return self._indicator(slug, "cci", params)

    def mfi(self, slug: str, **params: Any) -> Any:
        """Money Flow Index."""
        return self._indicator(slug, "mfi", params)

    def williams_r(self, slug: str, **params: Any) -> Any:
        """Williams %R."""
        return self._indicator(slug, "williams-r", params)

    def price_volatility(self, slug: str, **params: Any) -> Any:
        """Price volatility."""
        return self._indicator(slug, "price-volatility", params)

    def volume_volatility(self, slug: str, **params: Any) -> Any:
        """Volume volatility."""
        return self._indicator(slug, "volume-volatility", params)

    def macd(self, slug: str, **params: Any) -> Any:
        """Moving Average Convergence Divergence."""
        return self._indicator(slug, "macd", params)

    def obv(self, slug: str, **params: Any) -> Any:
        """On-Balance Volume."""
        return self._indicator(slug, "obv", params)

    def adx(self, slug: str, **params: Any) -> Any:
        """Average Directional Index."""
        return self._indicator(slug, "adx", params)

    def vwap(self, slug: str, **params: Any) -> Any:
        """Volume-Weighted Average Price."""
        return self._indicator(slug, "vwap", params)

    def cmf(self, slug: str, **params: Any) -> Any:
        """Chaikin Money Flow."""
        return self._indicator(slug, "cmf", params)


class CalculatorsResource(Resource):
    """Financial calculators."""

    def dca(self, **params: Any) -> Any:
        """Dollar-cost-averaging calculator. Params: slug, amount, interval, start, end, series."""
        return self._http.get("/api/v1/calculators/dca", params)

    def profit_loss(self, **params: Any) -> Any:
        """Profit / loss calculator. Params: slug, amount, buy_date, sell_date, buy_fee, sell_fee."""
        return self._http.get("/api/v1/calculators/profit-loss", params)

    def compound_interest(self, **params: Any) -> Any:
        """Compound interest calculator. Params: principal, rate, duration, duration_unit,
        compound_frequency, contribution, contribution_frequency.

        ``rate`` is the annual nominal rate in %; each compounding period earns
        ``rate`` divided by the periods per year.
        """
        return self._http.get("/api/v1/calculators/compound-interest", params)

    def loan(self, **params: Any) -> Any:
        """Loan-vs-sell calculator. Params: slug, crypto_amount, needed_cash, term_months,
        interest_rate, ltv, expected_growth, tax_rate."""
        return self._http.get("/api/v1/calculators/loan", params)

    def staking(self, **params: Any) -> Any:
        """Staking rewards calculator. Params: amount, period, period_unit, apy,
        compound_frequency, commission."""
        return self._http.get("/api/v1/calculators/staking", params)
