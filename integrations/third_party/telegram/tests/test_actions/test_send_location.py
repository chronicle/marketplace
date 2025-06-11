from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ..common import CONFIG_PATH
from ..core.session import TelegramSession
from ..core.product import Telegram
from ...actions.SendLocation import main as SendLocation


class TestSendLocation:
    CHAT_ID = "123456789"
    LATITUDE = "34.0522"
    LONGITUDE = "-118.2437"

    @set_metadata(
        parameters={"Chat ID": CHAT_ID, "Latitude": LATITUDE, "Longitude": LONGITUDE},
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_location_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SendLocation()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/sendLocation")
        assert request.kwargs["params"] == {
            "chat_id": self.CHAT_ID,
            "latitude": self.LATITUDE,
            "longitude": self.LONGITUDE,
        }

        assert (
            action_output.results.output_message == "The location was sent successfully"
        )
        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert action_output.results.json_output.json_result == {
            "ok": True,
            "result": {
                "chat_id": self.CHAT_ID,
                "latitude": self.LATITUDE,
                "longitude": self.LONGITUDE,
            },
        }

    @set_metadata(
        parameters={"Chat ID": CHAT_ID, "Latitude": LATITUDE, "Longitude": LONGITUDE},
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_location_failure(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
        telegram: Telegram,
    ) -> None:
        with telegram.fail_requests():
            SendLocation()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/sendLocation")
        assert request.kwargs["params"] == {
            "chat_id": self.CHAT_ID,
            "latitude": self.LATITUDE,
            "longitude": self.LONGITUDE,
        }

        assert (
            action_output.results.output_message
            == "Could not sent location. Error: b'Mock API failure'"
        )
        assert action_output.results.execution_state == ExecutionState.FAILED
