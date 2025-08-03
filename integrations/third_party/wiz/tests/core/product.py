from __future__ import annotations

from typing import TYPE_CHECKING

# from Tests.mocks.product import MockProduct
from .. import common

if TYPE_CHECKING:
    from collections.abc import Iterable, MutableMapping
    from TIPCommon.types import SingleJson
    from Integrations.Wiz.Managers.datamodels import Issue


class Wiz:
    def __init__(self) -> None:
        self._issues: MutableMapping[str, Issue] = {}
        self._comments: MutableMapping[str, common.Comment] = {}

    def add_issue(self, issue: Issue) -> None:
        self._issues[issue.issue_id] = issue

    def get_issue(self, issue_id: str) -> Issue:
        return self._issues[issue_id]

    def get_issues(self) -> Iterable[Issue]:
        return list(self._issues.values())

    def get_comment(self, issue_id: str) -> SingleJson:
        return self._comments[issue_id]

    def add_comment(self, comment: common.Comment) -> None:
        self._comments[comment.issue_id] = comment

    def cleanup_issues(self) -> None:
        self._issues = {}
