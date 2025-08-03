from __future__ import annotations

from typing import TYPE_CHECKING

from TIPCommon.base.action import Action
from TIPCommon.extraction import extract_action_param

from core import action_init
from core import api_manager
from core import constants
from core import exceptions

if TYPE_CHECKING:
    from typing import NoReturn
    from TIPCommon.types import SingleJson
    from core import datamodels


class GetIssueDetails(Action):
    def __init__(self) -> None:
        super().__init__(constants.GET_ISSUE_DETAILS_SCRIPT_NAME)

    def _extract_action_parameters(self) -> None:
        self.params.issue_id = extract_action_param(
            self.soar_action,
            param_name="Issue ID",
            is_mandatory=True,
            print_value=True,
        )

    def _init_api_clients(self) -> api_manager.ApiManager:
        return action_init.create_api_client(self.soar_action)

    def _perform_action(self, _) -> None:
        self.json_results: SingleJson = self._get_issue_details().to_json()
        self.output_message: str = (
            "Successfully returned information about the issue "
            f"{self.params.issue_id} in {constants.INTEGRATION_NAME}."
        )

    def _get_issue_details(self) -> datamodels.Issue:
        try:
            return self.api_client.get_issue_details(issue_id=self.params.issue_id)

        except exceptions.IssueNotFoundError as e:
            raise exceptions.IssueNotFoundError(
                f"Issue with ID {self.params.issue_id} wasn't found in "
                f"{constants.INTEGRATION_NAME}."
            ) from e


def main() -> NoReturn:
    GetIssueDetails().run()


if __name__ == "__main__":
    main()
