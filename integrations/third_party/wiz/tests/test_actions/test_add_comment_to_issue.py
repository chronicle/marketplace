from __future__ import annotations

from typing import TYPE_CHECKING

import copy

from TIPCommon.base.action import ExecutionState
from TIPCommon.base.data_models import ActionJsonOutput, ActionOutput
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from actions import add_comment_to_issue
from core import constants, data_parser
from .. import common
from tests.core.product import Wiz
from tests.core.session import WizSession

if TYPE_CHECKING:
    from collections.abc import Mapping
    from core import datamodels


ISSUE: datamodels.Issue = common.ISSUE
JSON_OUTPUT_RESULT: datamodels.Issue = data_parser.build_issue_comment_object(
    common.ADD_COMMENT_TO_ISSUE
)

SUCCESS_OUTPUT_MESSAGE: str = (
    f"Successfully added a comment to the issue with ID {ISSUE.issue_id} in "
    f"{constants.INTEGRATION_NAME}."
)
FAILED_OUTPUT_MESSAGE: str = (
    f'Error executing action "{constants.ADD_COMMENT_TO_ISSUE_SCRIPT_NAME}"\nReason: '
    f"Issue with ID {common.INVALID_ISSUE_ID} wasn't found in "
    f"{constants.INTEGRATION_NAME}."
)

DEFAULT_PARAMETERS: Mapping[str, str] = {
    "Issue ID": ISSUE.issue_id,
    "Comment": common.TEST_COMMENT,
}
FAILED_PARAMETERS: Mapping[str, str] = copy.deepcopy(DEFAULT_PARAMETERS)
FAILED_PARAMETERS["Issue ID"] = common.INVALID_ISSUE_ID


@set_metadata(integration_config=common.CONFIG, parameters=DEFAULT_PARAMETERS)
def test_add_comment_to_issue_action_success(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue: datamodels.Issue = copy.deepcopy(ISSUE)
    issue_id: str = issue.issue_id
    comment = common.Comment(
        issue_id=issue_id,
        comment=common.TEST_COMMENT,
    )
    wiz.add_issue(issue)
    wiz.add_comment(comment)
    add_comment_to_issue.main()

    assert comment.is_comment is True
    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=SUCCESS_OUTPUT_MESSAGE,
        result_value=True,
        execution_state=ExecutionState.COMPLETED,
        json_output=ActionJsonOutput(json_result=JSON_OUTPUT_RESULT.to_json()),
    )


@set_metadata(integration_config=common.CONFIG, parameters=FAILED_PARAMETERS)
def test_add_comment_to_issue_action_failure(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue: datamodels.Issue = copy.deepcopy(ISSUE)
    issue.issue_id: str = common.INVALID_ISSUE_ID
    wiz.add_issue(issue)
    add_comment_to_issue.main()

    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=FAILED_OUTPUT_MESSAGE,
        result_value=False,
        execution_state=ExecutionState.FAILED,
        json_output=None,
    )
