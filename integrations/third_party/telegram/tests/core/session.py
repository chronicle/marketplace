from __future__ import annotations

from typing import Any

from integrations.third_party.telegram.tests.core.telegram import Telegram

from packages.integration_testing.src.integration_testing.request import MockRequest
from packages.integration_testing.src.integration_testing import router
from packages.integration_testing.src.integration_testing.requests.response import MockResponse
from packages.integration_testing.src.integration_testing.requests.session import MockSession, RouteFunction


class TelegramSession(MockSession[MockRequest, MockResponse, Telegram]):

    def get_routed_functions(self) -> list[RouteFunction]:
        return [
            self.send_message
        ]

    @router.get(r"/bot\S+/sendMessage")
    def send_message(self, request: MockRequest) -> MockResponse:
        payload: dict[str, Any] = request.kwargs["params"]
        chat_id = payload["chat_id"]
        text = payload["text"]
        
        response_data = self._product.send_message(chat_id, text)
        return MockResponse(content=response_data)