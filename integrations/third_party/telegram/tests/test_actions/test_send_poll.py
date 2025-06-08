from __future__ import annotations

from TIPCommon.base.action import ExecutionState

from integrations.third_party.telegram.actions.SendPoll import main as SendPoll
from integrations.third_party.telegram.tests.common import CONFIG_PATH
from integrations.third_party.telegram.tests.core.session import TelegramSession
from integrations.third_party.telegram.tests.core.telegram import Telegram
from packages.integration_testing.src.integration_testing.platform.script_output import (
    MockActionOutput,
)
from packages.integration_testing.src.integration_testing.set_meta import set_metadata


class TestSendPoll:
    CHAT_ID = "123456789"
    QUESTION = "What is your favorite color?"
    OPTIONS = "Red,Blue,Green"
    IS_ANONYMOUS = "True"

    @set_metadata(
        parameters={
            "Chat ID": CHAT_ID,
            "Question": QUESTION,
            "Options": OPTIONS,
            "Is Anonymous": IS_ANONYMOUS,
        },
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_poll_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SendPoll()

        # Assert that the correct API call was made
        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/sendPoll")
        assert request.kwargs["params"] == {
            "chat_id": self.CHAT_ID,
            "question": self.QUESTION,
            "options": self.OPTIONS,
            "is_anonymous": self.IS_ANONYMOUS,
        }

        assert (
            action_output.results.output_message
            == f'The poll "{self.QUESTION}" was sent successfully.'
        )
        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert action_output.results.json_output.json_result == {
            "ok": True,
            "result": {
                "chat_id": self.CHAT_ID,
                "question": self.QUESTION,
                "options": self.OPTIONS,
                "is_anonymous": self.IS_ANONYMOUS,
            },
        }

    @set_metadata(
        parameters={
            "Chat ID": CHAT_ID,
            "Question": QUESTION,
            "Options": OPTIONS,
            "Is Anonymous": IS_ANONYMOUS,
        },
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_poll_failure(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
        telegram: Telegram,
    ) -> None:
        telegram.fail_next_call()
        SendPoll()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/sendPoll")
        assert request.kwargs["params"] == {
            "chat_id": self.CHAT_ID,
            "question": self.QUESTION,
            "options": self.OPTIONS,
            "is_anonymous": self.IS_ANONYMOUS,
        }

        assert (
            action_output.results.output_message
            == "Could not send poll. Error: b'Simulated API failure for SendPoll'"
        )
        assert action_output.results.execution_state == ExecutionState.FAILED
