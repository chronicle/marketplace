from __future__ import annotations

import datetime as dt
from urllib.parse import urljoin
from typing import Any

import requests
from typing import Any as _Any

from .constants import RESOURCE_AUDIENCE


class AzureMonitorClient:
    def __init__(
        self,
        authenticated_session: requests.Session,
        login_api_root: str,
        api_root: str,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        verify_ssl: bool,
        logger: _Any,
    ) -> None:
        self.session: requests.Session = authenticated_session
        self.session.verify = verify_ssl
        self.login_api_root: str = login_api_root.rstrip("/") + "/"
        self.api_root: str = api_root.rstrip("/") + "/"
        self.tenant_id: str = tenant_id
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self._access_token: str | None = None
        self.logger: _Any = logger

    def _obtain_token(self) -> str:
        token_url: str = urljoin(
            self.login_api_root, f"{self.tenant_id}/oauth2/token"
        )
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "resource": RESOURCE_AUDIENCE,
        }
        self.logger.info("Requesting Azure Monitor access token")
        resp = self.session.post(token_url, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        if resp.status_code != 200:
            # Try to extract best error message
            message = None
            try:
                message = resp.json().get("error_description")
            except Exception:  # noqa: BLE001
                message = resp.text
            raise requests.HTTPError(f"Failed to obtain access token: {resp.status_code} {message}")
        token: str = resp.json().get("access_token", "")
        if not token:
            raise requests.HTTPError("No access_token in token response")
        self._access_token = token
        return token

    def _get_token(self) -> str:
        return self._access_token or self._obtain_token()

    def _auth_headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._get_token()}"}

    def query_logs(
        self,
        workspace_id: str,
        query: str,
        timespan: tuple[dt.datetime, dt.datetime] | None,
        max_rows: int,
    ) -> requests.Response:
        url: str = urljoin(self.api_root, f"v1/workspaces/{workspace_id}/query")
        payload: dict[str, Any] = {
            "query": query,
            "maxRows": max_rows,
        }
        if timespan is not None:
            start, end = timespan
            payload["timespan"] = f"{start.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z/{end.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z"
        headers = {"Content-Type": "application/json"}
        headers.update(self._auth_headers())
        self.logger.info("Executing Azure Monitor query", extra={"url": url, "maxRows": max_rows})
        return self.session.post(url, json=payload, headers=headers)

    @staticmethod
    def compute_timespan(
        timeframe: str | None,
        start_time: str | None,
        end_time: str | None,
        now: dt.datetime | None = None,
    ) -> tuple[dt.datetime, dt.datetime] | None:
        if timeframe is None:
            return None
        tf = timeframe.lower()
        ref: dt.datetime = now or dt.datetime.utcnow()
        if tf == "last hour":
            return ref - dt.timedelta(hours=1), ref
        if tf == "last 6 hours":
            return ref - dt.timedelta(hours=6), ref
        if tf == "last 24 hours":
            return ref - dt.timedelta(hours=24), ref
        if tf == "last week":
            return ref - dt.timedelta(days=7), ref
        if tf == "last month":
            return ref - dt.timedelta(days=30), ref
        if tf == "custom":
            if not start_time:
                raise ValueError("Start Time is required when Time Frame is Custom")
            start_dt = dt.datetime.fromisoformat(start_time.replace("Z", "+00:00")).replace(tzinfo=None)
            end_dt = (
                dt.datetime.fromisoformat(end_time.replace("Z", "+00:00")).replace(tzinfo=None)
                if end_time
                else ref
            )
            return start_dt, end_dt
        return None

    @staticmethod
    def tables_to_rows(json_body: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        tables = json_body.get("tables") or []
        if not tables:
            return results
        table = tables[0]
        columns = [c.get("name") for c in table.get("columns", [])]
        for row in table.get("rows", []) or []:
            results.append({k: v for k, v in zip(columns, row, strict=False)})
        return results
