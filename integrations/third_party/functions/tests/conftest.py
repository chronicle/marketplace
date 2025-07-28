import pytest
from .core.session import TestSession

@pytest.fixture
def session() -> TestSession:
    return TestSession()

