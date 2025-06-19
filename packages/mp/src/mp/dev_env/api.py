import base64
from pathlib import Path

import requests


class BackendAPI:
    def __init__(self, api_root: str, username: str, password: str):
        self.api_root = api_root.rstrip("/")
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None

    def login(self):
        login_url = f"{self.api_root}/api/external/v1/accounts/Login?format=camel"
        login_payload = {"userName": self.username, "password": self.password}
        resp = self.session.post(login_url, json=login_payload, verify=False)
        resp.raise_for_status()
        self.token = resp.json()["token"]
        self.session.headers.update({"Authorization": f"Bearer {self.token}"})

    def get_integration_details(self, zip_path: Path):
        details_url = (
            f"{self.api_root}/api/external/v1/ide/GetPackageDetails?format=camel"
        )
        with open(zip_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        details_payload = {"data": data}
        resp = self.session.post(details_url, json=details_payload, verify=False)
        resp.raise_for_status()
        return resp.json()

    def upload_integration(self, zip_path: Path, integration_id: str):
        upload_url = f"{self.api_root}/api/external/v1/ide/ImportPackage?format=camel"
        with open(zip_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        upload_payload = {
            "data": data,
            "integrationIdentifier": integration_id,
            "isCustom": False,
        }
        resp = self.session.post(upload_url, json=upload_payload, verify=False)
        resp.raise_for_status()
        return resp.json()
