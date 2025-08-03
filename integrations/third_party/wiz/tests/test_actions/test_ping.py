from __future__ import annotations

from typing import TYPE_CHECKING

import copy

from TIPCommon.base.action import ExecutionState
from TIPCommon.base.data_models import ActionOutput
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from actions import ping
from core import constants
from .. import common
from tests.core.product import Wiz
from tests.core.session import WizSession

if TYPE_CHECKING:
    from core import datamodels


ISSUE: datamodels.Issue = common.ISSUE

PING_SUCCESS_MESSAGE: str = (
    f"Successfully connected to the {constants.INTEGRATION_NAME} "
    "server with the provided connection parameters!"
)
FAILED_OUTPUT_MESSAGE: str = (
    "Failed to connect to the Wiz server!\nReason: Invalid credentials provided. "
    "Please check the integration configuration."
)


@set_metadata(integration_config=common.CONFIG)
def test_ping_success(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue: datamodels.Issue = copy.deepcopy(ISSUE)
    wiz.add_issue(issue)
    ping.main()

    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=PING_SUCCESS_MESSAGE,
        result_value=True,
        execution_state=ExecutionState.COMPLETED,
        json_output=None,
    )


@set_metadata(integration_config=common.CONFIG)
def test_ping_failure(
    wiz: Wiz,
    script_session: WizSession,
    action_output: MockActionOutput,
) -> None:
    wiz.cleanup_issues()
    issue: datamodels.Issue = copy.deepcopy(ISSUE)
    issue.issue_id = common.INVALID_TOKEN_ID
    wiz.add_issue(issue)
    ping.main()

    assert len(script_session.request_history) == 2
    assert action_output.results == ActionOutput(
        output_message=FAILED_OUTPUT_MESSAGE,
        result_value=False,
        execution_state=ExecutionState.FAILED,
        json_output=None,
    )
