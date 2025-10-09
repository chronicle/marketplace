from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from TIPCommon.extraction import extract_action_param

from ..core.base_action import AzureAction
from ..core.integration_client import AzureMonitorClient

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson


class SearchLogs(AzureAction):
    def __init__(self) -> None:
        super().__init__("Search Logs")
        self.json_results: SingleJson | None = None

    def _extract_action_parameters(self) -> None:
        self.params.workspace_id = extract_action_param(
            self.soar_action,
            param_name="Workspace ID",
            print_value=True,
        )
        self.params.query = extract_action_param(
            self.soar_action,
            param_name="Query",
            is_mandatory=True,
            print_value=True,
        )
        self.params.time_frame = extract_action_param(
            self.soar_action,
            param_name="Time Frame",
            default_value="Last Hour",
            input_type=str,
            print_value=True,
        )
        self.params.start_time = extract_action_param(
            self.soar_action,
            param_name="Start Time",
            print_value=True,
        )
        self.params.end_time = extract_action_param(
            self.soar_action,
            param_name="End Time",
            print_value=True,
        )
        self.params.max_results = int(
            extract_action_param(
                self.soar_action,
                param_name="Max Results To Return",
                default_value=100,
                input_type=int,
                is_mandatory=True,
                print_value=True,
            )
        )
        if self.params.max_results > 1000:
            self.params.max_results = 1000

    def _init_api_clients(self) -> AzureMonitorClient:
        return super()._init_api_clients()

    def _perform_action(self, _) -> None:
        client: AzureMonitorClient = self.api_client
        if client is None:
            client = self._init_api_clients()
            self.api_client = client

        cfg = self.soar_action.get_configuration("AzureMonitor")
        workspace_id: str = self.params.workspace_id or cfg.get("Workspace ID")

        timespan = AzureMonitorClient.compute_timespan(
            self.params.time_frame,
            self.params.start_time,
            self.params.end_time,
        )

        response = client.query_logs(
            workspace_id=workspace_id,
            query=self.params.query,
            timespan=timespan,
            max_rows=self.params.max_results,
        )

        if response.status_code == 200:
            rows = AzureMonitorClient.tables_to_rows(response.json())
            self.json_results = rows  # type: ignore[assignment]
            found = len(rows) > 0
            self.result_value = True
            if found:
                self.output_message = (
                    f"Successfully returned results for the query \"{self.params.query}\" in Azure Monitor."
                )
            else:
                self.output_message = (
                    f"No results were found for the query \"{self.params.query}\" in Azure Monitor"
                )
            return

        # Non-200 responses
        try:
            body = response.json()
        except Exception:  # noqa: BLE001
            body = {}
        if response.status_code == 404:
            msg = body.get("message") or response.text
            raise RuntimeError(f"Error executing action \"Search Logs\". Reason: {msg}")
        if response.status_code == 400:
            inner = body.get("innererror", {}).get("innererror", {}).get("message")
            raise RuntimeError(f"Error executing action \"Search Logs\". Reason: {inner}")

        response.raise_for_status()


def main() -> NoReturn:
    SearchLogs().run()


if __name__ == "__main__":
    main()
