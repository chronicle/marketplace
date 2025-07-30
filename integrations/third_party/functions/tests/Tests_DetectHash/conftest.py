from collections.abc import Iterator

import pytest

from integrations.third_party.functions.core.session import MockSdkSession

pytest_plugins = ("integration_testing.conftest",)


@pytest.fixture(autouse=True)
def sdk_session() -> Iterator[MockSdkSession]:
    yield MockSdkSession()