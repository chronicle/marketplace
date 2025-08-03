from __future__ import annotations

from typing import TYPE_CHECKING
import copy

import pytest
from core import constants
from . import common

if TYPE_CHECKING:
    from core.api_manager import ApiManager
    from core.datamodels import Issue
    from tests.core.product import Wiz
    from tests.core.session import WizSession


ISSUE: Issue = common.ISSUE


class TestApiManager:
    """Unit tests for Integration's ApiManager methods."""

    def test_ping_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test ping success.

        Verify that the test_connectivity method successfully pings the Wiz API and
        returns a 200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: Issue = copy.deepcopy(ISSUE)
        wiz.add_issue(issue)

        manager.test_connectivity()

        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200

    def test_ping_failure_invalid_token(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test ping failure due to invalid token.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: Issue = copy.deepcopy(ISSUE)
        issue.issue_id: str = common.INVALID_TOKEN_ID
        wiz.add_issue(issue)
        with pytest.raises(Exception) as e:
            manager.test_connectivity()

        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 401
        assert script_session.request_history[0].response.json() == common.INVALID_TOKEN
        assert type(e.value).__name__ == "InvalidCredsError"
        assert "Invalid credentials provided. Please check the integration configuration." in str(
            e.value
        )

    def test_get_issue_details_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test get issue details success.

        Verify that the get_issue_details method successfully retrieves issue details
        and returns a 200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: Issue = copy.deepcopy(ISSUE)
        issue_id: str = issue.issue_id
        wiz.add_issue(issue)

        manager.get_issue_details(issue_id=issue_id)

        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == {
            "data": {"issue": issue.to_json()}
        }

    def test_get_issue_details_failure(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test get issue details failure due to invalid token.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: Issue = copy.deepcopy(ISSUE)
        issue.issue_id: str = common.INVALID_ISSUE_ID
        wiz.add_issue(issue)
        with pytest.raises(Exception) as e:
            manager.test_connectivity()

        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == common.INVALID_ISSUE
        assert type(e.value).__name__ == "IssueNotFoundError"
        assert "id must be a valid service issue id" in str(e.value)

    def test_add_comment_to_issue_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test add comment to issue success.

        Verify that the add_comment_to_issue method successfully adds a comment to an
        issue and returns a 200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: Issue = copy.deepcopy(ISSUE)
        issue_id: str = issue.issue_id
        comment: common.Comment = common.Comment(
            issue_id=issue_id,
            comment=common.TEST_COMMENT,
        )
        wiz.add_issue(issue)
        wiz.add_comment(comment)

        manager.add_comment_to_issue(
            issue_id=issue_id,
            comment=comment.comment,
        )

        assert comment.is_comment is True
        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == common.ADD_COMMENT_TO_ISSUE

    def test_reopen_issue_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test reopen issue success.

        Verify that the reopen_issue method successfully reopens an issue and returns a
        200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: common.IssueStatus = common.IssueStatus(issue_id="test_issue_id")
        issue_id = issue.issue_id
        wiz.add_issue(issue)

        manager.reopen_issue(issue_id=issue_id)

        assert issue.status == constants.STATUS_REOPEN
        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == common.REOPEN_ISSUE

    def test_ignore_issue_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test reopen issue success.

        Verify that the reopen_issue method successfully reopens an issue and returns a
        200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: common.IssueStatus = common.IssueStatus(issue_id="test_issue_id")
        issue_id: str = issue.issue_id
        wiz.add_issue(issue)

        manager.ignore_issue(
            issue_id=issue_id,
            resolution_reason="False Positive",
            note="Test ignore note",
        )

        assert issue.status == constants.STATUS_REJECTED
        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == common.IGNORE_ISSUE

    def test_resolve_issue_success(
        self,
        manager: ApiManager,
        wiz: Wiz,
        script_session: WizSession,
    ) -> None:
        """Test reopen issue success.

        Verify that the reopen_issue method successfully reopens an issue and returns a
        200 status code.

        Args:
            manager (ApiManager): ApiManager object.
            wiz (Wiz): Wiz product object.
            script_session (WizSession): WizSession object.
        """
        wiz.cleanup_issues()
        issue: common.IssueStatus = common.IssueStatus(issue_id="test_issue_id")
        issue_id: str = issue.issue_id
        wiz.add_issue(issue)

        manager.resolve_issue(
            issue_id=issue_id,
            resolution_note="Test resolution note",
            resolution_reason="Malicious Threat",
        )

        assert issue.status == constants.STATUS_RESOLVED
        assert len(script_session.request_history) == 1
        assert script_session.request_history[0].response.status_code == 200
        assert script_session.request_history[0].response.json() == common.RESOLVE_ISSUE
