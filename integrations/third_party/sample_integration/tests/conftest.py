from __future__ import annotations

import pytest
from integration_testing.common import use_live_api
from TIPCommon.base.utils import CreateSession

from .core.product import VatComply
from .core.session import VatComplySession

pytest_plugins = ("integration_testing.conftest",)


@pytest.fixture
def vatcomply() -> VatComply:
    return VatComply()


@pytest.fixture(autouse=True)
def script_session(
    monkeypatch: pytest.MonkeyPatch,
    vatcomply: VatComply,
) -> VatComplySession:
    """Mock VatComply scripts' session and get back an object to view request history"""
    session: VatComplySession = VatComplySession(vatcomply)

    if not use_live_api():
        monkeypatch.setattr(CreateSession, "create_session", lambda: session)
        monkeypatch.setattr("requests.Session", lambda: session)

    return session
