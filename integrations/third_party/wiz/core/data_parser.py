from __future__ import annotations

from typing import TYPE_CHECKING

from . import datamodels

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson


def build_issue_object(issue_json: SingleJson) -> datamodels.Issue:
    """Build an Issue object from the provided JSON data.

    Args:
        issue_json (SingleJson): The JSON data containing issue details.

    Returns:
        datamodels.Issue: An Issue object containing the details of the issue.
    """
    return datamodels.Issue.from_json(issue_json.get("data", {}).get("issue", {}))


def build_update_issue_object(issue_json: SingleJson) -> datamodels.Issue:
    """Build an Update Issue object from the provided JSON data.

    Args:
        issue_json (SingleJson): The JSON data containing updated issue details.

    Returns:
        datamodels.Issue: An Issue object containing the details of the updated issue.
    """
    return datamodels.Issue.from_json(
        issue_json.get("data", {}).get("updateIssue", {}).get("issue", {})
    )


def build_issue_comment_object(issue_json: SingleJson) -> datamodels.IssueComment:
    """Build an Issue Comment object from the provided JSON data.

    Args:
        issue_json (SingleJson): The JSON data containing commented issue details.

    Returns:
        datamodels.Issue: An Issue object containing the details of the commented issue.
    """
    return datamodels.IssueComment.from_json(
        issue_json.get("data", {}).get("createIssueNote", {}).get("issueNote", {})
    )
