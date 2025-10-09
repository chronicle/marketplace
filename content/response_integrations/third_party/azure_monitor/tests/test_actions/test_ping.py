from __future__ import annotations

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from TIPCommon.base.action import ExecutionState

from azure_monitor.actions import ping as ping_action
from ..common import CONFIG_PATH
from ..core.product import AzureMonitorProduct
from ..core.session import AzureMonitorSession


class TestPing:
    @set_metadata(integration_config_file_path=CONFIG_PATH)
    def test_ping_success(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # Provide an empty but OK tables response for the ping query
        product.query_tables = [
            {
                "name": "PrimaryResult",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {"name": "OperationName", "type": "string"},
                ],
                "rows": [],
            }
        ]

        ping_action.main()

        # Expect two requests: token and query
        assert len(script_session.request_history) == 2
        assert script_session.request_history[0].request.url.path.endswith("/oauth2/token")
        assert script_session.request_history[1].request.url.path.endswith("/query")

        assert (
            action_output.results.output_message
            == "Successfully connected to the Azure Monitor server with the provided connection parameters!"
        )
        assert action_output.results.execution_state == ExecutionState.COMPLETED

    @set_metadata(integration_config_file_path=CONFIG_PATH)
    def test_ping_failure(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # Simulate token failure
        with product.fail_token():
            ping_action.main()

        # Token request attempted
        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].request.url.path.endswith("/oauth2/token")

        assert action_output.results.output_message == "Failed to connect to the Azure Monitor server!"
        assert action_output.results.execution_state == ExecutionState.FAILED
