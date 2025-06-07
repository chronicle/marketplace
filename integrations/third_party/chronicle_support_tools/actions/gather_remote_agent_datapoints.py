from __future__ import annotations

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core import constants
from ..core.action_base_class import ActionBaseClass, ActionResult
from ..core.agent_load_info_collector import (
    AgentLoadInfoCollector,
    CollectFileInformation,
)
from ..core.collect_agent_logs import CollectAgentLogs
from ..core.ra_logs_collector import RALogsCollector
from ..core.utils import ChronicleSOARCommons


class GatherRemoteAgentLogs(ActionBaseClass):
    def __init__(self, siemplify):
        super().__init__(siemplify)

    def _extract_action_configuration(self):
        self.params.integrationName = ChronicleSOARCommons.extract_action_param(
            siemplify=self.siemplify,
            param_name="IntegrationName",
            is_mandatory=True,
            default_value=constants.EMPTY_STRING,
            print_value=True,
        )

        self.params.connectorName = ChronicleSOARCommons.extract_action_param(
            siemplify=self.siemplify,
            param_name="ConnectorName",
            is_mandatory=False,
            default_value=constants.EMPTY_STRING,
            print_value=True,
        )

    def _perform_action(self) -> ActionResult:
        status = EXECUTION_STATE_FAILED

        try:
            RALogCollector_ = RALogsCollector(
                self.params.integrationName,
                self.siemplify,
            )
            RALogCollector_.log_collected_info()

            AgentLoadInfoCollector_ = AgentLoadInfoCollector(
                self.params.integrationName,
                self.siemplify,
            )
            AgentLoadInfoCollector_.log_collected_info()

            CollectFileInformation_ = CollectFileInformation(
                self.params.integrationName,
                self.siemplify,
            )
            CollectFileInformation_.log_collected_info()

            CollectAgentLogs_ = CollectAgentLogs(
                self.params.integrationName,
                self.params.connectorName,
                self.siemplify,
            )
            CollectAgentLogs_.log_collected_info()

            status = EXECUTION_STATE_COMPLETED

        except Exception as e:
            status = EXECUTION_STATE_FAILED
            raise e

        return ActionResult(status, True)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = constants.GATHER_AGENT_DATA_SCRIPT_NAME
    action = GatherRemoteAgentLogs(siemplify)
    action.run()


if __name__ == "__main__":
    main()
