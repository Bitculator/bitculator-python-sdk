import unittest

from bitculator import (
    APIError,
    AuthenticationError,
    BitculatorError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    ServerError,
    ValidationError,
)

from ._doubles import http_error, make_client, raw_http_error


def envelope(code, message, details=None):
    return {"error": {"code": code, "message": message, "details": details}}


def one_shot(*steps):
    """A client that never retries, so every status maps straight to its error."""
    client, _ = make_client(*steps, max_retries=0)
    return client


class ErrorsTest(unittest.TestCase):
    def test_maps_statuses_to_the_typed_hierarchy(self):
        cases = [
            (401, AuthenticationError),
            (403, PermissionDeniedError),
            (404, NotFoundError),
            (422, ValidationError),
            (429, RateLimitError),
            (500, ServerError),
            (503, ServerError),
        ]
        for status, expected in cases:
            with self.subTest(status=status):
                client = one_shot(http_error(status, envelope("some_code", f"status {status}")))
                with self.assertRaises(expected) as ctx:
                    client.coins.get("bitcoin")
                self.assertIsInstance(ctx.exception, BitculatorError)
                self.assertEqual(ctx.exception.status, status)

    def test_unmapped_4xx_falls_back_to_plain_api_error(self):
        client = one_shot(http_error(418, envelope("teapot", "I am a teapot")))
        with self.assertRaises(APIError) as ctx:
            client.coins.get("bitcoin")
        self.assertIs(type(ctx.exception), APIError)

    def test_carries_code_message_and_details_from_the_envelope(self):
        details = {"per_page": ["must not be greater than 100"]}
        client = one_shot(http_error(422, envelope("validation_failed", "Invalid parameters.", details)))
        with self.assertRaises(ValidationError) as ctx:
            client.coins.get("bitcoin")
        self.assertEqual(ctx.exception.code, "validation_failed")
        self.assertEqual(ctx.exception.message, "Invalid parameters.")
        self.assertEqual(ctx.exception.details, details)

    def test_falls_back_to_top_level_message_then_http_status(self):
        client = one_shot(http_error(500, {"message": "Whoops."}))
        with self.assertRaises(ServerError) as ctx:
            client.coins.get("bitcoin")
        self.assertEqual(ctx.exception.message, "Whoops.")

        client = one_shot(raw_http_error(502, "Bad Gateway"))
        with self.assertRaises(ServerError) as ctx:
            client.coins.get("bitcoin")
        self.assertEqual(ctx.exception.message, "HTTP 502")
        self.assertIsNone(ctx.exception.code)

    def test_captures_the_request_id_header(self):
        client = one_shot(http_error(500, envelope("server_error", "boom"), {"X-Request-Id": "req_123"}))
        with self.assertRaises(ServerError) as ctx:
            client.coins.get("bitcoin")
        self.assertEqual(ctx.exception.request_id, "req_123")

    def test_rate_limit_error_exposes_retry_after(self):
        client = one_shot(http_error(429, envelope("rate_limited", "Slow down"), {"Retry-After": "30"}))
        with self.assertRaises(RateLimitError) as ctx:
            client.coins.get("bitcoin")
        self.assertEqual(ctx.exception.retry_after, 30)

    def test_retry_after_is_none_when_absent_or_unparsable(self):
        client = one_shot(http_error(429, envelope("rate_limited", "Slow down")))
        with self.assertRaises(RateLimitError) as ctx:
            client.coins.get("bitcoin")
        self.assertIsNone(ctx.exception.retry_after)

        client = one_shot(http_error(429, envelope("rate_limited", "Slow down"), {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"}))
        with self.assertRaises(RateLimitError) as ctx:
            client.coins.get("bitcoin")
        self.assertIsNone(ctx.exception.retry_after)


if __name__ == "__main__":
    unittest.main()
