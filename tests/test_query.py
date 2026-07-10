import unittest
import urllib.parse

from ._doubles import make_client, ok


def query_for(**params):
    client, opener = make_client(ok({"data": []}))
    client.coins._http.get("/api/v1/coins", params)
    parts = urllib.parse.urlsplit(opener.calls[0].url)
    return urllib.parse.parse_qs(parts.query)


class QueryTest(unittest.TestCase):
    def test_trailing_underscore_is_stripped_from_reserved_words(self):
        query = query_for(from_="2026-01-01", to="2026-02-01")
        self.assertEqual(query["from"], ["2026-01-01"])
        self.assertEqual(query["to"], ["2026-02-01"])
        self.assertNotIn("from_", query)

    def test_lists_serialize_to_csv(self):
        query = query_for(symbols=["btc", "eth", "sol"])
        self.assertEqual(query["symbols"], ["btc,eth,sol"])

    def test_none_and_empty_lists_are_dropped(self):
        query = query_for(locale=None, symbols=[], page=1)
        self.assertNotIn("locale", query)
        self.assertNotIn("symbols", query)
        self.assertEqual(query["page"], ["1"])

    def test_booleans_serialize_lowercase(self):
        query = query_for(include_inactive=True, compact=False)
        self.assertEqual(query["include_inactive"], ["true"])
        self.assertEqual(query["compact"], ["false"])

    def test_tiny_floats_expand_to_plain_decimals(self):
        query = query_for(min_price=1e-7, max_price=-2.5e-8)
        self.assertEqual(query["min_price"], ["0.0000001"])
        self.assertEqual(query["max_price"], ["-0.000000025"])

    def test_huge_floats_expand_to_plain_decimals(self):
        query = query_for(min_marketcap=1e21)
        self.assertEqual(query["min_marketcap"], ["1000000000000000000000"])

    def test_ordinary_numbers_keep_their_shortest_form(self):
        query = query_for(min_price=0.1, page=42)
        self.assertEqual(query["min_price"], ["0.1"])
        self.assertEqual(query["page"], ["42"])

    def test_no_params_means_no_query_string(self):
        client, opener = make_client(ok({"data": []}))
        client.coins._http.get("/api/v1/coins")
        self.assertNotIn("?", opener.calls[0].url)


if __name__ == "__main__":
    unittest.main()
