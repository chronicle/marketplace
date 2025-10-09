from __future__ import annotations

import pytest
from integration_testing.common import use_live_api
from TIPCommon.base.utils import CreateSession

from .core.product import AzureMonitorProduct
from .core.session import AzureMonitorSession

pytest_plugins = ("integration_testing.conftest",)


@pytest.fixture
def product() -> AzureMonitorProduct:
    return AzureMonitorProduct()


@pytest.fixture(autouse=True)
def script_session(
    monkeypatch: pytest.MonkeyPatch,
    product: AzureMonitorProduct,
) -> AzureMonitorSession:
    """Mock Azure Monitor scripts' session and get back an object to view request history"""
    session: AzureMonitorSession = AzureMonitorSession(product)

    if not use_live_api():
        monkeypatch.setattr(CreateSession, "create_session", lambda: session)
        monkeypatch.setattr("requests.Session", lambda: session)

    return session
