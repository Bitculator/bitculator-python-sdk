# Bitculator Data API — Python SDK

[bitculator.com](https://bitculator.com) · [API documentation](https://bitculator.com/en/documentation/api/v1) · [Get an API key](https://bitculator.com/user/developer/api)
[PyPI — `bitculator`](https://pypi.org/project/bitculator/) · [GitHub](https://github.com/Bitculator/bitculator-python-sdk)

The official Python SDK for the [Bitculator Data API](https://bitculator.com).
Zero dependencies (standard-library only), typed, works on Python 3.9+.

> Keep your API key server-side. It is a Bearer token with the `data-api` ability
> and is not meant for client-side embedding.

## Install

```bash
pip install bitculator
```

## Quick start

```python
import os
from bitculator import Bitculator

client = Bitculator(os.environ["BITCULATOR_API_KEY"])

# Single resource — the {"data": ...} envelope is unwrapped for you.
bitcoin = client.coins.get("bitcoin")
print(bitcoin["price"])   # "63520.780763913" — a decimal string, never rounded

# A paginated list.
page = client.coins.list(per_page=50, sort="-marketcap")
print(page.data, page.meta["total"])
```

## Prices are decimal strings

Prices, rates, and supplies come back as **strings** (e.g. `"63520.780763913"`)
to preserve full precision. Use `decimal.Decimal` if you need to do math — do
**not** pass them through `float()`, which silently loses precision.

## Pagination

Every paginated method returns a `Page`. Read one page, or iterate to walk them all:

```python
# One page at a time.
page = client.exchanges.list(per_page=100)
while page is not None:
    for exchange in page.data:
        print(exchange["name"])
    page = page.next_page()

# Or auto-paginate across every page (iterating a Page walks all pages).
for coin in client.coins.list(sort="-marketcap"):
    print(coin["symbol"])
```

## Errors

Every failure derives from `BitculatorError`; HTTP failures raise a status-specific
subclass carrying the `{"error": {"code", "message", "details"}}` envelope.

```python
from bitculator import ValidationError, RateLimitError, APIError

try:
    client.coins.list(per_page=9999)  # over the plan cap -> 422
except ValidationError as err:
    print(err.code, err.details)
except RateLimitError as err:
    print("retry after", err.retry_after)
except APIError as err:
    print(err.status, err.message)
```

| Status | Exception |
| ------ | --------- |
| 401 | `AuthenticationError` |
| 403 | `PermissionDeniedError` (plan does not include this endpoint) |
| 404 | `NotFoundError` |
| 422 | `ValidationError` (`.details` holds the field errors) |
| 429 | `RateLimitError` (`.retry_after`) |
| 5xx | `ServerError` |

Timeouts raise `APITimeoutError`; network failures raise `APIConnectionError`.

## Quota

Every response carries `X-Quota-*` headers, surfaced on the client after each call:

```python
client.coins.list()
print(client.quota)   # Quota(limit=..., remaining=..., reset=..., raw={...})
```

## Configuration

```python
Bitculator(
    api_key,                          # required (positional)
    base_url="https://bitculator.com",  # default
    timeout=30.0,                     # seconds, default
    max_retries=2,                    # auto-retry 429 / 5xx / network; 0 to disable
)
```

## Passing parameters

Query parameters are keyword arguments and mirror the API's names exactly
(`per_page`, `min_price`, ...). For the reserved word `from` (in `convert`), pass
`from_` — the SDK maps it back to `from` on the wire:

```python
client.conversion.convert(from_="btc", to="usd", amount=1)
```

## Resources

`coins` · `prices` · `markets` · `exchanges` · `wallets` · `global_market` ·
`sentiment` · `indicators` · `liquidations` · `conversion` · `calculators` ·
`editorial` · `alarms` · `webhooks` · `meta`

Full endpoint reference: <https://bitculator.com/en/documentation/api/v1>.

## License

MIT
