from __future__ import annotations

from typing import TYPE_CHECKING

import dataclasses
import pathlib

from integration_testing.common import get_def_file_content

from core import data_parser

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson
    from core import datamodels


CONFIG_PATH: pathlib.Path = pathlib.Path(__file__).parent / "config.json"
CONFIG: SingleJson = get_def_file_content(CONFIG_PATH)
MOCK_PATH: pathlib.Path = pathlib.Path(__file__).parent / "mock_data.json"
MOCK_DATA: SingleJson = get_def_file_content(MOCK_PATH)
GET_ISSUE_DETAILS: SingleJson = MOCK_DATA["get_issue_details"]
ADD_COMMENT_TO_ISSUE: SingleJson = MOCK_DATA["add_comment_to_issue"]
IGNORE_ISSUE: SingleJson = MOCK_DATA["ignore_issue"]
REOPEN_ISSUE: SingleJson = MOCK_DATA["reopen_issue"]
RESOLVE_ISSUE: SingleJson = MOCK_DATA["resolve_issue"]
VALID_TOKEN: SingleJson = MOCK_DATA["valid_token"]
INVALID_TOKEN: SingleJson = MOCK_DATA["invalid_token"]
INVALID_ALERT: SingleJson = MOCK_DATA["invalid_alert"]
INVALID_ISSUE: SingleJson = MOCK_DATA["invalid_issue"]
INVALID_ISSUE_ID: str = "99999999"
INVALID_TOKEN_ID: str = "invalid_token"

GET_ISSUE_QUERY_NAME: str = "GetIssue"
ADD_COMMENT_QUERY_NAME: str = "CreateIssueComment"
UPDATE_ISSUE_QUERY_NAME: str = "UpdateIssue"
TEST_COMMENT: str = "Test comment for issue"

ISSUE: datamodels.Issue = data_parser.build_issue_object(GET_ISSUE_DETAILS)


@dataclasses.dataclass(slots=True)
class Comment:
    """Comment data model."""

    issue_id: str
    comment: str
    is_comment: bool = False


@dataclasses.dataclass(slots=True)
class IssueStatus:
    """Reopen issue data model."""

    issue_id: str
    status: str = None
