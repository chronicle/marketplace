from __future__ import annotations

import contextlib
import dataclasses
from typing import Any

from TIPCommon.types import SingleJson


@dataclasses.dataclass(slots=True)
class AzureMonitorProduct:
    """Simulated Azure Monitor backend for black-box tests."""

    # Configuration / state for responses
    last_query_payload: dict[str, Any] | None = None
    token_should_fail: bool = False
    query_should_fail: bool = False
    query_status_code: int = 200

    # Predefined responses
    token_response: SingleJson | None = dataclasses.field(default_factory=lambda: {"access_token": "mock-token"})
    query_tables: SingleJson | None = None

    @contextlib.contextmanager
    def fail_token(self):
        self.token_should_fail = True
        try:
            yield
        finally:
            self.token_should_fail = False

    @contextlib.contextmanager
    def fail_query(self, status_code: int = 500):
        self.query_should_fail = True
        self.query_status_code = status_code
        try:
            yield
        finally:
            self.query_should_fail = False
            self.query_status_code = 200

    def issue_token(self) -> tuple[int, SingleJson]:
        if self.token_should_fail:
            return 401, {"error_description": "invalid_client"}
        return 200, (self.token_response or {"access_token": "mock-token"})

    def query_logs(self, payload: dict[str, Any]) -> tuple[int, SingleJson]:
        self.last_query_payload = payload
        if self.query_should_fail:
            # 400 and 404 have specific handling in action code
            if self.query_status_code == 400:
                return 400, {"innererror": {"innererror": {"message": "Bad request sample"}}}
            if self.query_status_code == 404:
                return 404, {"message": "Not found sample"}
            return self.query_status_code, {"error": "Server error"}
        # Default successful response with provided tables or empty
        if self.query_tables is not None:
            return 200, {"tables": self.query_tables}
        return 200, {"tables": []}
