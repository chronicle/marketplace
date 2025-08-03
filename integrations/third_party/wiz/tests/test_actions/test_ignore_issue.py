from __future__ import annotations

from typing import TYPE_CHECKING

import copy

from TIPCommon.base.action import ExecutionState
from TIPCommon.base.data_models import ActionJsonOutput, ActionOutput
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from actions import ignore_issue
from core import constants, data_parser
from .. import common
from tests.core.product import Wiz
from tests.core.session import WizSession

if TYPE_CHECKING:
    from collections.abc import Mapping
    from core import datamodels


ISSUE_ID: str = "test_id"
JSON_RESULT_OBJECT: datamodels.Issue = data_parser.build_update_issue_object(common.IGNORE_ISSUE)

SUCCESS_OUTPUT_MESSAGE: str = (
    f"Successfully ignored issue with ID {ISSUE_ID} in {constants.INTEGRATION_NAME}."
)
FAILED_OUTPUT_MESSAGE: str = (
    f'Error executing action "{constants.IGNORE_ISSUE_SCRIPT_NAME}"\nReason: '
    f"Issue with ID {common.INVALID_ISSUE_ID} wasn't found in "
    f"{constants.INTEGRATION_NAME}."
)

DEFAULT_PARAMETERS: Mapping[str, str] = {
    "Issue ID": ISSUE_ID,
    "Resolution Reason": constants.DEFAULT_IGNORE_ISSUE_RESOLUTION_REASON,
    "Resolution Note": "Test ignore note",
}
FAILED_PARAMETERS: Mapping[str, str] = copy.deepcopy(DEFAULT_PARAMETERS)
FAILED_PARAMETERS["Issue ID"] = common.INVALID_ISSUE_ID


@set_metadata(integration_config=common.CONFIG, parameters=DEFAULT_PARAMETERS)
def test_ignore_issue_action_success(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue = common.IssueStatus(issue_id=ISSUE_ID)
    wiz.add_issue(issue)
    ignore_issue.main()

    assert issue.status == constants.STATUS_REJECTED
    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=SUCCESS_OUTPUT_MESSAGE,
        result_value=True,
        execution_state=ExecutionState.COMPLETED,
        json_output=ActionJsonOutput(json_result=JSON_RESULT_OBJECT.to_json()),
    )


@set_metadata(integration_config=common.CONFIG, parameters=FAILED_PARAMETERS)
def test_ignore_issue_action_failure(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue = common.IssueStatus(issue_id=common.INVALID_ISSUE_ID)
    wiz.add_issue(issue)
    ignore_issue.main()

    assert issue.status is None
    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=FAILED_OUTPUT_MESSAGE,
        result_value=False,
        execution_state=ExecutionState.FAILED,
        json_output=None,
    )
