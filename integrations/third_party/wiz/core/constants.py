from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


INTEGRATION_NAME: str = "Wiz"
PING_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Ping"
GET_ISSUE_DETAILS_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Get Issue Details"
ADD_COMMENT_TO_ISSUE_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Add Comment To Issue"
IGNORE_ISSUE_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Ignore Issue"
REOPEN_ISSUE_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Reopen Issue"
RESOLVE_ISSUE_SCRIPT_NAME: str = f"{INTEGRATION_NAME} - Resolve Issue"


ENDPOINTS: Mapping[str, str] = {
    "graphql": "/graphql",
}

AUTH_URL: str = "https://auth.app.wiz.io/oauth/token"

STATUS_REJECTED: str = "REJECTED"
STATUS_REOPEN: str = "OPEN"
STATUS_RESOLVED: str = "RESOLVED"
DEFAULT_IGNORE_ISSUE_RESOLUTION_REASON: str = "False Positive"
IGNORE_ISSUE_RESOLUTION_REASONS: Mapping[str, str] = {
    "False Positive": "FALSE_POSITIVE",
    "Exception": "EXCEPTION",
    "Won't Fix": "WONT_FIX",
}
DEFAULT_RESOLVE_ISSUE_RESOLUTION_REASON: str = "Malicious Threat"
RESOLVE_ISSUE_RESOLUTION_REASONS: Mapping[str, str] = {
    "Malicious Threat": "MALICIOUS_THREAT",
    "Not Malicious Threat": "NOT_MALICIOUS_THREAT",
    "Security Test Threat": "SECURITY_TEST_THREAT",
    "Planned Action Threat": "PLANNED_ACTION_THREAT",
    "Inconclusive Threat": "INCONCLUSIVE_THREAT",
}
ISSUE_NOT_FOUND_ERRORS: Sequence[str] = ["id must be a valid service issue id"]
UNAUTHORIZED_STATUS_CODE: int = 401
