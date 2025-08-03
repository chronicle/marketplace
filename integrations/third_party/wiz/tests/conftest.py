from __future__ import annotations

import pytest

from TIPCommon.base.utils import CreateSession
from integration_testing.common import use_live_api
from integration_testing.request import MockRequest
from integration_testing.requests.response import MockResponse
from integration_testing.logger import Logger

from .common import CONFIG
from .core.product import Wiz
from .core.session import WizSession
from core.api_manager import ApiManager, ApiParameters


pytest_plugins = ("integration_testing.conftest",)


@pytest.fixture(name="wiz")
def wiz_product() -> Wiz:
    yield Wiz()


@pytest.fixture(name="script_session", autouse=True)
def wiz_script_session(
    monkeypatch: pytest.MonkeyPatch,
    wiz: Wiz,
) -> WizSession:
    """Create script session"""
    session: WizSession[MockRequest, MockResponse, Wiz] = WizSession(wiz)
    if not use_live_api():
        monkeypatch.setattr(CreateSession, "create_session", lambda *_: session)

    yield session


@pytest.fixture(name="manager")
def wiz_manager(script_session: WizSession) -> ApiManager:
    """Wiz manager"""
    api_root: str = CONFIG["API Root"]

    logger = Logger()
    api_params: ApiParameters = ApiParameters(api_root)

    yield ApiManager(script_session, api_params, logger)
