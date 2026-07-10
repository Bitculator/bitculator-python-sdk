"""
Run with: BITCULATOR_API_KEY=... python examples/quickstart.py
(against local dev, add BITCULATOR_BASE_URL=http://localhost)
"""

import os

from bitculator import APIError, Bitculator

client = Bitculator(
    os.environ.get("BITCULATOR_API_KEY", ""),
    base_url=os.environ.get("BITCULATOR_BASE_URL", "https://bitculator.com"),
)


def main() -> None:
    client.meta.ping()

    # Single resource — the {"data": ...} envelope is unwrapped for you.
    bitcoin = client.coins.get("bitcoin")
    print("BTC price:", bitcoin["price"])  # "63520.780763913" — a decimal string, never rounded

    # Top 5 coins by marketcap.
    top = client.coins.list(per_page=5, sort="-marketcap")
    for coin in top.data:
        print(f"#{coin['rank']}", coin["symbol"], coin["price"])

    # Auto-paginate the first ~40 gainers.
    for i, coin in enumerate(client.coins.gainers(per_page=20)):
        print("gainer:", coin["symbol"], coin["change_24h"])
        if i >= 39:
            break

    # A technical indicator.
    print("RSI(14):", client.indicators.rsi("bitcoin", period=14))
    print("quota:", client.quota)


if __name__ == "__main__":
    try:
        main()
    except APIError as err:
        print(f"API {err.status}: {err.code} {err.message}")
