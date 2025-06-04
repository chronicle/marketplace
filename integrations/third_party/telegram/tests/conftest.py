from __future__ import annotations

import pytest
from TIPCommon.base.utils import CreateSession

from integrations.third_party.telegram.tests.core.session import TelegramSession
from integrations.third_party.telegram.tests.core.telegram import Telegram
from packages.integration_testing.src.integration_testing.common import use_live_api

pytest_plugins = (
    "packages.integration_testing.tests.test_integration_testing.conftest",
)

@pytest.fixture
def telegram() -> Telegram:
    yield Telegram()


@pytest.fixture(autouse=True)
def script_session(
    monkeypatch: pytest.MonkeyPatch,
    telegram: Telegram,
) -> TelegramSession:
    """Mock telegram scripts' session and get back an object to view request history"""
    session: TelegramSession = TelegramSession(telegram)

    if not use_live_api():
        monkeypatch.setattr(CreateSession, "create_session", lambda: session)
        monkeypatch.setattr("requests.Session", lambda: session)

    yield session
