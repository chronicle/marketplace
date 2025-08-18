from __future__ import annotations

from typing import Iterable

from integration_testing import router
from integration_testing.common import get_request_payload
from integration_testing.request import MockRequest
from integration_testing.requests.response import MockResponse
from integration_testing.requests.session import MockSession, Response, RouteFunction
from TIPCommon.types import SingleJson

from ..common import FULL_ALERT_DATA
from .product import VatComply


class VatComplySession(MockSession[MockRequest, MockResponse, VatComply]):
    def get_routed_functions(self) -> Iterable[RouteFunction[Response]]:
        return [
            self.get_rates,
            self.add_attachment,
            self.alert_details,
        ]

    @router.get(r"/rates")
    def get_rates(self, request: MockRequest) -> MockResponse:
        try:
            params: SingleJson = get_request_payload(request)
            base: str | None = params.get("base")
            symbols: str | None = params.get("symbols")
            date: str | None = params.get("date")
            rates = self._product.get_rates(base, symbols, date)

            return MockResponse(content=rates)
        except ValueError as e:
            return MockResponse(content=str(e), status_code=422)

    @router.post(r"/api/external/v1/sdk/AddAttachment")
    def add_attachment(self, _: MockRequest) -> MockResponse:
        return MockResponse(content={}, status_code=200)

    @router.post("/api/external/v1/sdk/AlertFullDetails")
    def alert_details(self, _) -> MockResponse:
        """Route /AlertFullDetails requests"""
        return MockResponse(content=FULL_ALERT_DATA, status_code=201)
