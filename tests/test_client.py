import unittest
import urllib.parse

from bitculator import Bitculator, BitculatorError, Page

from ._doubles import FakeOpener, make_client, ok


class ClientTest(unittest.TestCase):
    def test_requires_an_api_key(self):
        with self.assertRaisesRegex(BitculatorError, "api_key"):
            Bitculator("")

    def test_exposes_all_15_resource_groups(self):
        client, _ = make_client()
        groups = [
            "coins",
            "prices",
            "markets",
            "exchanges",
            "wallets",
            "global_market",
            "sentiment",
            "indicators",
            "liquidations",
            "conversion",
            "calculators",
            "editorial",
            "alarms",
            "webhooks",
            "meta",
        ]
        for group in groups:
            self.assertTrue(hasattr(client, group), f"client.{group} should exist")

    def test_list_methods_hit_api_v1_paths_and_return_a_page(self):
        client, opener = make_client(ok({"data": [{"id": 1}], "meta": {"current_page": 1, "last_page": 1}}))
        page = client.coins.list(per_page=1)
        self.assertIsInstance(page, Page)
        parts = urllib.parse.urlsplit(opener.calls[0].url)
        self.assertEqual(parts.path, "/api/v1/coins")
        self.assertTrue(opener.calls[0].url.startswith("https://api.test/"))

    def test_percent_encodes_dynamic_path_segments(self):
        client, opener = make_client(ok({"data": {}}))
        client.coins.get("weird/slug name")
        parts = urllib.parse.urlsplit(opener.calls[0].url)
        self.assertEqual(parts.path, "/api/v1/coins/weird%2Fslug%20name")

    def test_strips_trailing_slashes_from_a_custom_base_url(self):
        opener = FakeOpener([ok({"data": {}})])
        client = Bitculator("k", base_url="https://staging.test///", opener=opener)
        client.coins.get("bitcoin")
        self.assertTrue(opener.calls[0].url.startswith("https://staging.test/api/v1/coins/bitcoin"))

    def test_defaults_the_user_agent_to_bitculator_python(self):
        opener = FakeOpener([ok({"data": {}})])
        client = Bitculator("k", opener=opener)
        client.coins.get("bitcoin")
        self.assertRegex(opener.calls[0].header("user-agent"), r"^bitculator-python/\d+\.\d+\.\d+$")

    def test_quota_is_none_before_the_first_call_and_updates_after_each(self):
        client, _ = make_client(
            ok({"data": {}}, {"X-Quota-Limit": "10000", "X-Quota-Remaining": "9999"}),
            ok({"data": {}}, {"X-Quota-Limit": "10000", "X-Quota-Remaining": "9998"}),
        )
        self.assertIsNone(client.quota)
        client.coins.get("bitcoin")
        self.assertEqual(client.quota.remaining, 9999)
        client.coins.get("ethereum")
        self.assertEqual(client.quota.remaining, 9998)


if __name__ == "__main__":
    unittest.main()
