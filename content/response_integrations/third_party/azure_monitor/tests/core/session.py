from __future__ import annotations

from typing import Any

from integration_testing import router
from integration_testing.common import get_request_payload
from integration_testing.request import MockRequest
from integration_testing.requests.response import MockResponse
from integration_testing.requests.session import MockSession, RouteFunction

from .product import AzureMonitorProduct


class AzureMonitorSession(MockSession[MockRequest, MockResponse, AzureMonitorProduct]):
    def get_routed_functions(self) -> list[RouteFunction]:
        return [
            self.obtain_token,
            self.query_logs,
        ]

    @router.post(r"/[^/]+/oauth2/token")
    def obtain_token(self, request: MockRequest) -> MockResponse:
        try:
            status, body = self._product.issue_token()
            return MockResponse(content=body, status_code=status)
        except Exception as e:  # noqa: BLE001
            return MockResponse(content=str(e), status_code=500)

    @router.post(r"/v1/workspaces/[^/]+/query")
    def query_logs(self, request: MockRequest) -> MockResponse:
        try:
            payload: dict[str, Any] = get_request_payload(request)
            status, body = self._product.query_logs(payload)
            return MockResponse(content=body, status_code=status)
        except Exception as e:  # noqa: BLE001
            return MockResponse(content=str(e), status_code=500)
