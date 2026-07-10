from __future__ import annotations

from typing import Any, List, Union

from ..pagination import Page
from ._base import Resource


class AlarmsResource(Resource):
    """Price alarms owned by the API key."""

    def list(self, **params: Any) -> Page:
        """List your alarms (paginated). Params: page, per_page, status, direction, notification."""
        return self._http.get_page("/api/v1/alarms", params)

    def create(
        self,
        *,
        name: str,
        coin: str,
        metric: str,
        direction: str,
        target: float,
        notification: str,
    ) -> Any:
        """Create an alarm."""
        return self._http.post(
            "/api/v1/alarms",
            {
                "name": name,
                "coin": coin,
                "metric": metric,
                "direction": direction,
                "target": target,
                "notification": notification,
            },
        )

    def delete(self, id: Union[str, int]) -> Any:
        """Delete an alarm by id."""
        return self._http.delete(f"/api/v1/alarms/{self._enc(id)}")


class WebhooksResource(Resource):
    """Webhook endpoints and their delivery log."""

    def list(self) -> Any:
        """List your webhook endpoints."""
        return self._http.get("/api/v1/webhooks")

    def create(self, *, url: str, events: List[str]) -> Any:
        """Register a webhook endpoint for a set of events."""
        return self._http.post("/api/v1/webhooks", {"url": url, "events": events})

    def delete(self, id: Union[str, int]) -> Any:
        """Delete a webhook endpoint by id."""
        return self._http.delete(f"/api/v1/webhooks/{self._enc(id)}")

    def test(self, id: Union[str, int]) -> Any:
        """Send a test event to a webhook endpoint."""
        return self._http.post(f"/api/v1/webhooks/{self._enc(id)}/test")

    def deliveries(self, id: Union[str, int], **params: Any) -> Page:
        """Delivery log for a webhook endpoint (paginated). Params: page, per_page."""
        return self._http.get_page(f"/api/v1/webhooks/{self._enc(id)}/deliveries", params)


class MetaResource(Resource):
    """Service metadata: spec, health, and key usage."""

    def openapi(self) -> Any:
        """The raw OpenAPI specification for the API."""
        return self._http.get("/api/v1/openapi.json")

    def ping(self) -> Any:
        """Health check."""
        return self._http.get("/api/v1/ping")

    def usage(self) -> Any:
        """Current key usage and quota."""
        return self._http.get("/api/v1/usage")
