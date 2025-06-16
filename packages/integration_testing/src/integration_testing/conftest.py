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

import sys
from typing import TYPE_CHECKING

import pytest
import SiemplifyLogger
import SiemplifyUtils
from SiemplifyBase import SiemplifyBase
from SiemplifyConnectors import SiemplifyConnectorExecution
from TIPCommon.base.utils import CreateSession

from .common import use_live_api
from .logger import Logger
from .platform.external_context import MockExternalContext
from .platform.script_output import MockActionOutput, MockConnectorOutput
from .requests.session import MockSession

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture(autouse=True)
def script_session(
    monkeypatch: pytest.MonkeyPatch,
) -> MockSession:
    """Mock scripts' sessions and to view request and response history."""
    session: MockSession = MockSession()
    if not use_live_api():
        monkeypatch.setattr(CreateSession, "create_session", lambda: session)

    return session


@pytest.fixture(autouse=True)
def sdk_session(monkeypatch: pytest.MonkeyPatch) -> MockSession:
    """Automatic fixture used in tests to provide a mock HTTP session for SDK tests.

    It substitutes the real API call with a mocked session for test purposes unless
    the live API is explicitly used.

    Args:
        monkeypatch: A monkeypatch fixture used to dynamically modify or patch
            module or object attributes within the test session.

    Returns:
        MockSession: A custom session object used as a mock when interacting with
            the SDK during tests.

    """
    session: MockSession = MockSession()
    if not use_live_api():
        monkeypatch.setattr(SiemplifyBase, "create_session", lambda *_: session)

    return session


@pytest.fixture(autouse=True)
def mock_sys_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fixture to mock the `sys.exit` function with a no-operation lambda.

    This fixture is automatically used in all tests to prevent the actual
    termination of the Python interpreter when `sys.exit` is called during testing.

    Args:
        monkeypatch (pytest.MonkeyPatch): A pytest utility to set or alter
            attributes during tests.

    """
    monkeypatch.setattr(sys, "exit", lambda _: ...)


@pytest.fixture(autouse=True)
def mock_siemplify_logger(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the SiemplifyLogger class with a custom Logger.

    This fixture ensures that the Logger class replaces any references to the
    SiemplifyLogger class within the test environment. This is particularly useful for
    testing purposes where dependency injection or mocking is required.

    Args:
        monkeypatch: A special test object provided by pytest to temporarily
            modify or patch objects, methods, or properties.

    """
    monkeypatch.setattr(SiemplifyLogger, "SiemplifyLogger", Logger)


@pytest.fixture(autouse=True)
def mock_sys_argv(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock `sys.argv` for tests to provide custom arguments during test execution.

    This fixture is automatically used in tests.
    It replaces the `sys.argv` attribute with a predefined list of command-line
    arguments to simulate different runtime inputs.

    Args:
        monkeypatch: The pytest MonkeyPatch fixture used to modify or replace
            attributes dynamically during test execution.

    """
    monkeypatch.setattr(sys, "argv", ["", "True", ""])


@pytest.fixture(autouse=True)
def run_folder(monkeypatch: pytest.MonkeyPatch) -> None:
    """Automatically applied fixture to mock the `run_folder`.

    Mocking the method of the`SiemplifyConnectorExecution` class.
    This fixture ensures that the `run_folder`
    method always returns the string "run".

    Args:
        monkeypatch: A pytest fixture that enables monkeypatching
            of methods and properties during tests.

    """
    monkeypatch.setattr(SiemplifyConnectorExecution, "run_folder", lambda: "run")


@pytest.fixture
def action_output(monkeypatch: pytest.MonkeyPatch) -> Iterator[MockActionOutput]:
    """Fixture to provide a mock environment for capturing action output streams.

    It replaces the standard output and error streams with mock streams for testing.
    This fixture uses `MockActionOutput` to mock the output streams. It ensures that
    all standard output and standard errors are passed through the mock environment to
    allow validation and assertions on the output during tests.

    Args:
        monkeypatch: Pytest fixture used to modify or replace
            attributes and environment variables for testing purposes.

    Yields:
        Instance of `MockActionOutput` providing mock interfaces for
        capturing and validating standard output and error streams during tests.

    """
    with MockActionOutput() as output:
        monkeypatch.setattr(SiemplifyUtils, "real_stdout", output.get_out_io())
        monkeypatch.setattr(sys, "stderr", output.get_err_io())
        yield output


@pytest.fixture
def connector_output(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[MockConnectorOutput]:
    """Fixture for mocking and capturing connector output streams.

    This fixture temporarily replaces the real standard output and error streams used by
    the SiemplifyUtils class and the `sys` module with mocked IO streams.
    The replacement allows capturing and inspecting any outputs generated during the
    execution of a test that relies on this fixture.

    Args:
        monkeypatch: Object that facilitates dynamic modifications
            of attributes or dictionaries within the scope of the test.

    Yields:
        Instance of a mocked connector output that provides
        access to the captured standard output and error streams during the test.

    """
    with MockConnectorOutput() as output:
        monkeypatch.setattr(SiemplifyUtils, "real_stdout", output.get_out_io())
        monkeypatch.setattr(sys, "stderr", output.get_err_io())
        yield output


@pytest.fixture
def external_context() -> MockExternalContext:
    """External context DB-like object."""
    return MockExternalContext()
