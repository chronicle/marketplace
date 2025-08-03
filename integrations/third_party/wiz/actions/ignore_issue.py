from __future__ import annotations

from typing import TYPE_CHECKING

from TIPCommon.base.action import Action
from TIPCommon.extraction import extract_action_param
from TIPCommon.validation import ParameterValidator

from core import action_init
from core import api_manager
from core import constants
from core import exceptions

if TYPE_CHECKING:
    from typing import NoReturn
    from TIPCommon.types import SingleJson
    from core import datamodels


class RejectIssue(Action):
    def __init__(self) -> None:
        super().__init__(constants.IGNORE_ISSUE_SCRIPT_NAME)

    def _extract_action_parameters(self) -> None:
        self.params.issue_id = extract_action_param(
            self.soar_action,
            param_name="Issue ID",
            is_mandatory=True,
            print_value=True,
        )
        self.params.resolution_reason = extract_action_param(
            self.soar_action,
            param_name="Resolution Reason",
            is_mandatory=True,
            default_value=constants.DEFAULT_IGNORE_ISSUE_RESOLUTION_REASON,
            print_value=True,
        )
        self.params.resolution_note = extract_action_param(
            self.soar_action,
            param_name="Resolution Note",
            is_mandatory=True,
            print_value=True,
        )

    def _validate_params(self) -> None:
        validator = ParameterValidator(self.soar_action)
        validator.validate_ddl(
            param_name="Resolution Reason",
            value=self.params.resolution_reason,
            ddl_values=list(constants.IGNORE_ISSUE_RESOLUTION_REASONS.keys()),
            default_value=constants.DEFAULT_IGNORE_ISSUE_RESOLUTION_REASON,
        )

    def _init_api_clients(self) -> api_manager.ApiManager:
        return action_init.create_api_client(self.soar_action)

    def _perform_action(self, _) -> None:
        self.json_results: SingleJson = self._ignore_issue().to_json()
        self.output_message: str = (
            "Successfully ignored issue with ID "
            f"{self.params.issue_id} in {constants.INTEGRATION_NAME}."
        )

    def _ignore_issue(self) -> datamodels.Issue:
        try:
            return self.api_client.ignore_issue(
                issue_id=self.params.issue_id,
                resolution_reason=self.params.resolution_reason,
                note=self.params.resolution_note,
            )

        except exceptions.IssueNotFoundError as e:
            raise exceptions.IssueNotFoundError(
                f"Issue with ID {self.params.issue_id} wasn't found in "
                f"{constants.INTEGRATION_NAME}."
            ) from e


def main() -> NoReturn:
    RejectIssue().run()


if __name__ == "__main__":
    main()
