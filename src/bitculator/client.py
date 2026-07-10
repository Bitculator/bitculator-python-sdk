from __future__ import annotations

import urllib.request

from ._http import HttpClient, Quota
from ._version import __version__
from .errors import BitculatorError
from .resources import (
    AlarmsResource,
    CalculatorsResource,
    CoinsResource,
    ConversionResource,
    EditorialResource,
    ExchangesResource,
    GlobalMarketResource,
    IndicatorsResource,
    LiquidationsResource,
    MarketsResource,
    MetaResource,
    PricesResource,
    SentimentResource,
    WalletsResource,
    WebhooksResource,
)

DEFAULT_BASE_URL = "https://bitculator.com"


class Bitculator:
    """The Bitculator Data API client.

    >>> client = Bitculator(api_key="...")
    >>> bitcoin = client.coins.get("bitcoin")

    Each API group is an attribute on the client: ``client.coins``,
    ``client.prices``, ``client.exchanges``, and so on.

    Pass ``opener`` (a ``urllib.request.OpenerDirector``) to inject for
    proxies/custom handlers; every request then goes through it.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        max_retries: int = 2,
        user_agent: str | None = None,
        opener: urllib.request.OpenerDirector | None = None,
    ) -> None:
        if not api_key:
            raise BitculatorError("A Data API key is required: Bitculator(api_key=...)")

        self._quota: Quota | None = None
        http = HttpClient(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            max_retries=max_retries,
            user_agent=user_agent or f"bitculator-python/{__version__}",
            on_quota=self._set_quota,
            opener=opener,
        )

        self.coins = CoinsResource(http)
        self.prices = PricesResource(http)
        self.markets = MarketsResource(http)
        self.exchanges = ExchangesResource(http)
        self.wallets = WalletsResource(http)
        self.global_market = GlobalMarketResource(http)
        self.sentiment = SentimentResource(http)
        self.indicators = IndicatorsResource(http)
        self.liquidations = LiquidationsResource(http)
        self.conversion = ConversionResource(http)
        self.calculators = CalculatorsResource(http)
        self.editorial = EditorialResource(http)
        self.alarms = AlarmsResource(http)
        self.webhooks = WebhooksResource(http)
        self.meta = MetaResource(http)

    def _set_quota(self, quota: Quota) -> None:
        self._quota = quota

    @property
    def quota(self) -> Quota | None:
        """Quota (``X-Quota-*``) from the most recent response, or ``None`` before the first call."""
        return self._quota
