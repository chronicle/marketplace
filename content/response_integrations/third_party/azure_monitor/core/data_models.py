from __future__ import annotations

import dataclasses


@dataclasses.dataclass(slots=True)
class IntegrationParameters:
    login_api_root: str
    api_root: str
    tenant_id: str
    client_id: str
    client_secret: str
    workspace_id: str
    verify_ssl: bool


@dataclasses.dataclass(slots=True)
class ApiParameters:
    api_root: str
    workspace_id: str
