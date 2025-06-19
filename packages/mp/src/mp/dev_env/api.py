# Copyright (c) 2024, Your Company or Name
import base64
from pathlib import Path
from typing import Any

import requests


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
        resp = self.session.post(login_url, json=login_payload, verify=False)
        resp.raise_for_status()
        self.token = resp.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_integration_details(self, zip_path: Path) -> dict[str, Any]:
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
        resp = self.session.post(details_url, json=details_payload, verify=False)
        resp.raise_for_status()
        return resp.json()

    def upload_integration(self, zip_path: Path, integration_id: str) -> dict[str, Any]:
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
        resp = self.session.post(upload_url, json=upload_payload, verify=False)
        resp.raise_for_status()
        return resp.json()
