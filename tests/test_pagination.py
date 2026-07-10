import unittest
import urllib.parse

from ._doubles import make_client, ok


def page_body(rows, current_page, last_page):
    return {
        "data": [{"id": row} for row in rows],
        "meta": {"current_page": current_page, "last_page": last_page, "per_page": len(rows), "total": 6},
        "links": {"next": f"https://api.test/api/v1/coins?page={current_page + 1}" if current_page < last_page else None},
    }


def query_of(call):
    return urllib.parse.parse_qs(urllib.parse.urlsplit(call.url).query)


class PaginationTest(unittest.TestCase):
    def test_page_exposes_data_meta_and_links(self):
        client, _ = make_client(ok(page_body([1, 2], 1, 3)))
        page = client.coins.list(per_page=2)
        self.assertEqual([row["id"] for row in page.data], [1, 2])
        self.assertEqual(page.meta["current_page"], 1)
        self.assertTrue(page.has_more)
        self.assertEqual(len(page), 2)

    def test_last_page_has_no_more_and_next_page_is_none(self):
        client, _ = make_client(ok(page_body([5, 6], 3, 3)))
        page = client.coins.list()
        self.assertFalse(page.has_more)
        self.assertIsNone(page.next_page())

    def test_next_page_requests_the_following_page_and_preserves_the_query(self):
        client, opener = make_client(ok(page_body([1, 2], 1, 3)), ok(page_body([3, 4], 2, 3)))
        first = client.coins.list(per_page=2, sort="rank")
        second = first.next_page()
        self.assertEqual([row["id"] for row in second.data], [3, 4])
        query = query_of(opener.calls[1])
        self.assertEqual(query["page"], ["2"])
        self.assertEqual(query["per_page"], ["2"])
        self.assertEqual(query["sort"], ["rank"])

    def test_auto_paging_iter_walks_every_page_in_order(self):
        client, opener = make_client(
            ok(page_body([1, 2], 1, 3)),
            ok(page_body([3, 4], 2, 3)),
            ok(page_body([5, 6], 3, 3)),
        )
        page = client.coins.list(per_page=2)
        seen = [row["id"] for row in page.auto_paging_iter()]
        self.assertEqual(seen, [1, 2, 3, 4, 5, 6])
        self.assertEqual(len(opener.calls), 3)

    def test_iterating_the_page_walks_all_pages(self):
        client, _ = make_client(ok(page_body([1], 1, 2)), ok(page_body([2], 2, 2)))
        page = client.coins.list()
        self.assertEqual([row["id"] for row in page], [1, 2])

    def test_envelope_without_meta_or_links_is_a_safe_final_page(self):
        client, _ = make_client(ok({"data": [{"id": 9}]}))
        page = client.coins.list()
        self.assertEqual([row["id"] for row in page.data], [9])
        self.assertFalse(page.has_more)
        self.assertIsNone(page.next_page())

    def test_empty_data_yields_an_empty_page(self):
        client, _ = make_client(ok({"data": [], "meta": {"current_page": 1, "last_page": 1}, "links": {}}))
        page = client.coins.list()
        self.assertEqual(page.data, [])
        self.assertFalse(page.has_more)


if __name__ == "__main__":
    unittest.main()
