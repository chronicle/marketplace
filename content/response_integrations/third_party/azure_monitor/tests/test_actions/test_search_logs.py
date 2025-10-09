from __future__ import annotations

from typing import TYPE_CHECKING

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from TIPCommon.base.action import ExecutionState

from azure_monitor.actions import search_logs as search_logs_action
from ..common import CONFIG_PATH
from ..core.product import AzureMonitorProduct
from ..core.session import AzureMonitorSession

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson


DEFAULT_PARAMS: SingleJson = {
    "Query": "AzureActivity | project TimeGenerated, OperationName",
    "Max Results To Return": 2,
}


class TestSearchLogs:
    @set_metadata(integration_config_file_path=CONFIG_PATH, parameters=DEFAULT_PARAMS)
    def test_search_logs_found(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # Arrange a successful tables response with 2 rows
        product.query_tables = [
            {
                "name": "PrimaryResult",
                "columns": [
                    {"name": "TimeGenerated", "type": "datetime"},
                    {"name": "OperationName", "type": "string"},
                ],
                "rows": [
                    ["2025-10-07T06:44:40.4570918Z", "Update datascanners"],
                    ["2025-10-07T06:44:41.1760472Z", "Update datascanners"],
                ],
            }
        ]

        search_logs_action.main()

        # Expect 2 requests: token and query
        assert len(script_session.request_history) == 2
        # Verify payload
        payload = script_session.request_history[1].request.json
        assert payload["query"].startswith("AzureActivity")
        assert payload["maxRows"] == 2
        assert "timespan" in payload  # computed by client

        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert (
            action_output.results.output_message
            == 'Successfully returned results for the query "AzureActivity | project TimeGenerated, OperationName" in Azure Monitor.'
        )
        # JSON results must be normalized to list of dicts
        assert isinstance(action_output.results.json_result, list)
        assert len(action_output.results.json_result) == 2
        assert set(action_output.results.json_result[0].keys()) == {"TimeGenerated", "OperationName"}

    @set_metadata(integration_config_file_path=CONFIG_PATH, parameters=DEFAULT_PARAMS)
    def test_search_logs_not_found(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # No rows
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

        search_logs_action.main()

        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert (
            action_output.results.output_message
            == 'No results were found for the query "AzureActivity | project TimeGenerated, OperationName" in Azure Monitor'
        )

    @set_metadata(integration_config_file_path=CONFIG_PATH, parameters=DEFAULT_PARAMS)
    def test_search_logs_404(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # Simulate 404
        product.query_tables = None
        with product.fail_query(status_code=404):
            search_logs_action.main()

        assert action_output.results.execution_state == ExecutionState.FAILED
        assert (
            action_output.results.output_message
            == 'Error executing action "Search Logs". Reason: Not found sample'
        )

    @set_metadata(integration_config_file_path=CONFIG_PATH, parameters=DEFAULT_PARAMS)
    def test_search_logs_400(
        self,
        script_session: AzureMonitorSession,
        action_output: MockActionOutput,
        product: AzureMonitorProduct,
    ) -> None:
        # Simulate 400
        product.query_tables = None
        with product.fail_query(status_code=400):
            search_logs_action.main()

        assert action_output.results.execution_state == ExecutionState.FAILED
        assert (
            action_output.results.output_message
            == 'Error executing action "Search Logs". Reason: Bad request sample'
        )
