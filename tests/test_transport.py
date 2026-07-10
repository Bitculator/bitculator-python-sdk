import json
import unittest

from bitculator import APIDecodeError, BitculatorError

from ._doubles import make_client, ok, raw_response


class TransportTest(unittest.TestCase):
    def test_sends_bearer_auth_accept_and_user_agent(self):
        client, opener = make_client(ok({"data": {}}))
        client.coins.get("bitcoin")
        call = opener.calls[0]
        self.assertEqual(call.header("authorization"), "Bearer test-key")
        self.assertEqual(call.header("accept"), "application/json")
        self.assertEqual(call.header("user-agent"), "bitculator-python/test")
        self.assertIsNone(call.header("content-type"))
        self.assertEqual(call.timeout, 2.0)

    def test_post_sends_json_body_and_strips_trailing_underscores(self):
        client, opener = make_client(ok({"data": {}}))
        client.coins._http.post("/api/v1/alarms", {"asset_slug": "bitcoin", "from_": "2026-01-01"})
        call = opener.calls[0]
        self.assertEqual(call.method, "POST")
        self.assertEqual(call.header("content-type"), "application/json")
        self.assertEqual(json.loads(call.body), {"asset_slug": "bitcoin", "from": "2026-01-01"})

    def test_unencodable_body_raises_without_hitting_the_network(self):
        client, opener = make_client()
        with self.assertRaisesRegex(BitculatorError, "Failed to encode request body"):
            client.coins._http.post("/api/v1/alarms", {"bad": {1, 2, 3}})
        self.assertEqual(opener.calls, [])

    def test_unwraps_the_data_envelope(self):
        client, _ = make_client(ok({"data": {"name": "Bitcoin", "price": "67412.83451201"}}))
        coin = client.coins.get("bitcoin")
        self.assertEqual(coin["name"], "Bitcoin")
        self.assertEqual(coin["price"], "67412.83451201")

    def test_passes_through_bodies_without_a_data_key(self):
        client, _ = make_client(ok({"openapi": "3.0.0"}))
        spec = client.coins._http.get("/api/v1/openapi.json")
        self.assertEqual(spec, {"openapi": "3.0.0"})

    def test_empty_2xx_body_returns_none(self):
        client, _ = make_client(ok())
        self.assertIsNone(client.coins._http.delete("/api/v1/alarms/1"))

    def test_malformed_2xx_body_raises_decode_error(self):
        client, _ = make_client(raw_response("<html>gateway page</html>"))
        with self.assertRaises(APIDecodeError):
            client.coins.get("bitcoin")

    def test_parses_quota_headers(self):
        client, _ = make_client(
            ok({"data": []}, {"X-Quota-Limit": "10000", "X-Quota-Remaining": "9871", "X-Quota-Reset": "1720569600"})
        )
        client.coins.get("bitcoin")
        quota = client.quota
        self.assertEqual(quota.limit, 10000)
        self.assertEqual(quota.remaining, 9871)
        self.assertEqual(quota.reset, 1720569600)
        self.assertEqual(quota.raw["x-quota-limit"], "10000")

    def test_missing_quota_headers_parse_to_none(self):
        client, _ = make_client(ok({"data": []}))
        client.coins.get("bitcoin")
        quota = client.quota
        self.assertIsNone(quota.limit)
        self.assertIsNone(quota.remaining)
        self.assertIsNone(quota.reset)
        self.assertEqual(quota.raw, {})


if __name__ == "__main__":
    unittest.main()
