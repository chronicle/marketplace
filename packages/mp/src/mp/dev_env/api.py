# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Any

import requests

if TYPE_CHECKING:
    import pathlib


class BackendAPI:
    """Handles backend API operations for the dev environment."""

    def __init__(self, api_root: str, username: str, password: str) -> None:
        """Initialize the BackendAPI with credentials and API root."""
        self.api_root = api_root.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None

    def login(self) -> None:
        """Authenticate and store the session token."""
        login_url = f"{self.api_root}/api/external/v1/accounts/Login?format=camel"
        login_payload = {"userName": self.username, "password": self.password}
        resp = self.session.post(login_url, json=login_payload)
        resp.raise_for_status()
        self.token = resp.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_integration_details(self, zip_path: pathlib.Path) -> dict[str, Any]:
        """Get integration details from a zipped package.

        Args:
            zip_path: Path to the zipped integration package.

        Returns:
            dict: The integration details as returned by the backend.

        """
        details_url = (
            f"{self.api_root}/api/external/v1/ide/GetPackageDetails?format=camel"
        )
        data = base64.b64encode(zip_path.read_bytes()).decode()
        details_payload = {"data": data}
        resp = self.session.post(details_url, json=details_payload)
        resp.raise_for_status()
        return resp.json()

    def upload_integration(
        self, zip_path: pathlib.Path, integration_id: str
    ) -> dict[str, Any]:
        """Upload a zipped integration package to the backend.

        Args:
            zip_path: Path to the zipped integration package.
            integration_id: The identifier of the integration.

        Returns:
            dict: The backend response after uploading the integration.

        """
        upload_url = f"{self.api_root}/api/external/v1/ide/ImportPackage?format=camel"
        data = base64.b64encode(zip_path.read_bytes()).decode()
        upload_payload = {
            "data": data,
            "integrationIdentifier": integration_id,
            "isCustom": False,
        }
        resp = self.session.post(upload_url, json=upload_payload)
        resp.raise_for_status()
        return resp.json()
