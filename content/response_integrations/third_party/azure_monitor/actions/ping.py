from __future__ import annotations

from typing import TYPE_CHECKING, NoReturn

from ..core.base_action import AzureAction
from ..core.integration_client import AzureMonitorClient

if TYPE_CHECKING:
    pass


SUCCESS_MESSAGE: str = (
    "Successfully connected to the Azure Monitor server with the provided connection parameters!"
)
ERROR_MESSAGE: str = "Failed to connect to the Azure Monitor server!"


class Ping(AzureAction):
    def __init__(self) -> None:
        super().__init__("Ping")
        self.output_message: str = SUCCESS_MESSAGE
        self.error_output_message: str = ERROR_MESSAGE
        self.api_client: AzureMonitorClient | None = None

    def _perform_action(self, _=None) -> None:
        self.api_client = self._init_api_clients()
        # Build a last-hour timespan and minimal query
        timespan = AzureMonitorClient.compute_timespan("Last Hour", None, None)
        # Use workspace from config
        workspace_id: str = self.soar_action.get_configuration("AzureMonitor").get("Workspace ID")
        response = self.api_client.query_logs(
            workspace_id=workspace_id,
            query="AzureActivity",
            timespan=timespan,
            max_rows=1,
        )
        if response.status_code != 200:
            response.raise_for_status()


def main() -> NoReturn:
    Ping().run()


if __name__ == "__main__":
    main()
