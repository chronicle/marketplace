from __future__ import annotations

from integrations.third_party.telegram.actions.SendMessage import main as SendMessage
from integrations.third_party.telegram.tests.common import CONFIG_PATH, TEST_BOT_TOKEN
from integrations.third_party.telegram.tests.core.session import TelegramSession
from packages.integration_testing.src.integration_testing.platform.external_context import MockExternalContext
from packages.integration_testing.src.integration_testing.platform.script_output import MockActionOutput
from packages.integration_testing.src.integration_testing.set_meta import set_metadata


class TestSendMessage:
    MESSAGE_CONTENT = "Hello, Telegram!"
    CHAT_ID = "123456789"

    @set_metadata(
        parameters={
            "Message": MESSAGE_CONTENT,
            "Chat ID": CHAT_ID
        },
        external_context=MockExternalContext(),
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_message_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SendMessage()

        # Assert that the correct API call was made
        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path == f"/bot{TEST_BOT_TOKEN}/sendMessage"
        assert request.kwargs["params"] == {"chat_id": self.CHAT_ID, "text": self.MESSAGE_CONTENT}

        assert action_output.output_message == "The message was sent successfully"
        assert action_output.results == {"ok": True, "result": {"chat_id": self.CHAT_ID, "text": self.MESSAGE_CONTENT}}

    @set_metadata(
        parameters={
            "Message": MESSAGE_CONTENT,
            "Chat ID": CHAT_ID
        },
        external_context=MockExternalContext(mock_api_failure=True),
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_message_failure(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SendMessage()

        # Assert that the correct API call was made
        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path == f"/bot{TEST_BOT_TOKEN}/sendMessage"
        assert request.kwargs["params"] == {"chat_id": self.CHAT_ID, "text": self.MESSAGE_CONTENT}

        assert action_output.output_message == "Could not send message. Error: Mock API failure"
        assert action_output.exception is not None
