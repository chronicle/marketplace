from __future__ import annotations

from TIPCommon.base.action import ExecutionState

from integrations.third_party.telegram.actions.Ping import main as Ping
from integrations.third_party.telegram.tests.common import CONFIG_PATH
from integrations.third_party.telegram.tests.core.session import TelegramSession
from integrations.third_party.telegram.tests.core.telegram import Telegram
from packages.integration_testing.src.integration_testing.platform.script_output import (
    MockActionOutput,
)
from packages.integration_testing.src.integration_testing.set_meta import set_metadata


class TestPing:
    @set_metadata(
        parameters={},
        integration_config_file_path=CONFIG_PATH,
    )
    def test_ping_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        Ping()

        # Assert that the correct API call was made
        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/getMe")

        assert action_output.results.output_message == "Connected successfully"
        assert action_output.results.execution_state == ExecutionState.COMPLETED

    @set_metadata(
        parameters={},
        integration_config_file_path=CONFIG_PATH,
    )
    def test_ping_failure(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
        telegram: Telegram,
    ) -> None:
        telegram.fail_next_call()
        Ping()

        # Assert that the correct API call was made
        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/getMe")

        assert action_output.results.output_message == "The Connection failed"
        assert action_output.results.execution_state == ExecutionState.FAILED
