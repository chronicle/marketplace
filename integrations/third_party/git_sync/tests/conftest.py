from __future__ import annotations

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def mock_siemplify():
    mock = MagicMock()
    mock.LOGGER = MagicMock()
    mock.RUN_FOLDER = "/tmp/test"
    mock.API_ROOT = "https://test.api"
    mock.api_key = "test_key"
    mock.script_name = ""
    mock.extract_job_param = MagicMock()
    mock.end_script = MagicMock()
    return mock


@pytest.fixture
def mock_git_client():
    mock = MagicMock()
    mock.clone = MagicMock()
    mock.pull = MagicMock()
    mock.commit = MagicMock()
    mock.push = MagicMock()
    return mock


@pytest.fixture
def mock_api_client():
    mock = MagicMock()
    mock.get_workflows = MagicMock(return_value=[])
    mock.create_workflow = MagicMock()
    mock.update_workflow = MagicMock()
    return mock


@pytest.fixture
def mock_cache():
    mock = MagicMock()
    mock.get = MagicMock(return_value=None)
    mock.set = MagicMock()
    mock.clear = MagicMock()
    return mock


@pytest.fixture
def temp_directory(tmp_path):
    return tmp_path