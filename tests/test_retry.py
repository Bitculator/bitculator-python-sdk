import time
import unittest
import urllib.error

from bitculator import APIConnectionError, APITimeoutError, ServerError

from ._doubles import http_error, make_client, ok


def fail(status, headers=None):
    return http_error(status, {"error": {"code": "err", "message": "nope"}}, headers)


class RetryTest(unittest.TestCase):
    def test_get_retries_a_5xx_and_succeeds(self):
        client, opener = make_client(fail(500), ok({"data": "ok"}))
        self.assertEqual(client.coins._http.get("/api/v1/coins"), "ok")
        self.assertEqual(len(opener.calls), 2)

    def test_get_retries_a_network_error_and_succeeds(self):
        client, opener = make_client(urllib.error.URLError(ConnectionRefusedError(111, "refused")), ok({"data": "ok"}))
        self.assertEqual(client.coins._http.get("/api/v1/coins"), "ok")
        self.assertEqual(len(opener.calls), 2)

    def test_delete_retries_a_5xx_and_succeeds(self):
        client, opener = make_client(fail(500), ok({"data": "ok"}))
        self.assertEqual(client.coins._http.delete("/api/v1/alarms/1"), "ok")
        self.assertEqual(len(opener.calls), 2)

    def test_post_never_retries_a_5xx(self):
        client, opener = make_client(fail(500), ok({"data": "ok"}))
        with self.assertRaises(ServerError):
            client.coins._http.post("/api/v1/alarms", {"asset_slug": "bitcoin"})
        self.assertEqual(len(opener.calls), 1)

    def test_post_never_retries_a_network_error(self):
        client, opener = make_client(urllib.error.URLError(ConnectionRefusedError(111, "refused")), ok({"data": "ok"}))
        with self.assertRaises(APIConnectionError):
            client.coins._http.post("/api/v1/alarms", {"asset_slug": "bitcoin"})
        self.assertEqual(len(opener.calls), 1)

    def test_post_does_retry_a_429(self):
        client, opener = make_client(fail(429), ok({"data": "ok"}))
        self.assertEqual(client.coins._http.post("/api/v1/alarms", {"asset_slug": "bitcoin"}), "ok")
        self.assertEqual(len(opener.calls), 2)

    def test_gives_up_after_max_retries(self):
        client, opener = make_client(fail(500), fail(500), fail(500), ok({"data": "ok"}), max_retries=2)
        with self.assertRaises(ServerError):
            client.coins._http.get("/api/v1/coins")
        self.assertEqual(len(opener.calls), 3)  # initial attempt + 2 retries; the queued 200 is never reached

    def test_honors_retry_after_seconds_on_a_429(self):
        client, opener = make_client(fail(429, {"Retry-After": "1"}), ok({"data": "ok"}))
        started = time.monotonic()
        self.assertEqual(client.coins._http.get("/api/v1/coins"), "ok")
        self.assertGreaterEqual(time.monotonic() - started, 0.9)
        self.assertEqual(len(opener.calls), 2)

    def test_timed_out_get_raises_after_exhausting_retries(self):
        client, opener = make_client(TimeoutError("timed out"), TimeoutError("timed out"), max_retries=1)
        with self.assertRaises(APITimeoutError):
            client.coins._http.get("/api/v1/coins")
        self.assertEqual(len(opener.calls), 2)  # the timeout is a transport failure, so the idempotent GET retried once

    def test_timed_out_post_raises_without_retrying(self):
        client, opener = make_client(TimeoutError("timed out"))
        with self.assertRaises(APITimeoutError):
            client.coins._http.post("/api/v1/alarms", {"asset_slug": "bitcoin"})
        self.assertEqual(len(opener.calls), 1)


if __name__ == "__main__":
    unittest.main()
