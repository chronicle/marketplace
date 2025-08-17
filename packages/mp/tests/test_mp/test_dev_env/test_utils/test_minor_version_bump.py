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

import json
import pathlib
import shutil

import pytest
import toml
import yaml

from mp.dev_env.utils import find_project_root, minor_version_bump

INTEGRATIONS_CACHE_FOLDER_PATH: pathlib.Path = find_project_root() / ".integrations_cache"

ORIG_BUILT_INTEGRATION_PATH = (
    pathlib.Path(__file__).parent.parent.parent
    / "mock_marketplace"
    / "mock_built_integration"
    / "mock_integration"
)
ORIG_NON_BUILT_INTEGRATION_PATH = (
    pathlib.Path(__file__).parent.parent.parent
    / "mock_marketplace"
    / "commercial"
    / "mock_integration"
)


@pytest.fixture
def sandbox(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    """
    Clone the two integration folders into a per-test sandbox.
    Returns a dict with convenient resolved paths inside the sandbox.

    pytest will delete tmp_path automatically at test end.
    """
    built_dst = tmp_path / "mock_built_integration" / "mock_integration"
    non_built_dst = tmp_path / "commercial" / "mock_integration"

    built_dst.parent.mkdir(parents=True, exist_ok=True)
    non_built_dst.parent.mkdir(parents=True, exist_ok=True)

    shutil.copytree(ORIG_BUILT_INTEGRATION_PATH, built_dst)
    shutil.copytree(ORIG_NON_BUILT_INTEGRATION_PATH, non_built_dst)

    return {
        "BUILT": built_dst,
        "NON_BUILT": non_built_dst,
        "DEF_FILE": built_dst / "Integration-mock_integration.def",
        "VERSION_CACHE": INTEGRATIONS_CACHE_FOLDER_PATH / "mock_integration" / "version_cache.yaml",
        "TMP_ROOT": tmp_path,
    }


class TestMinorVersionBump:
    def test_run_first_time_success(self, sandbox: dict[str, pathlib.Path]) -> None:
        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        assert INTEGRATIONS_CACHE_FOLDER_PATH.exists()
        assert sandbox["VERSION_CACHE"].exists()
        assert _load_cached_version(sandbox["VERSION_CACHE"]) == 2.2
        assert _load_built_version(sandbox["DEF_FILE"]) == 2.2

    def test_dependencies_not_changed_success(self, sandbox: dict[str, pathlib.Path]) -> None:
        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        old_version_cached = _load_cached_version(sandbox["VERSION_CACHE"])
        old_version_def_file = _load_built_version(sandbox["DEF_FILE"])

        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        assert _load_cached_version(sandbox["VERSION_CACHE"]) == old_version_cached
        assert _load_built_version(sandbox["DEF_FILE"]) == old_version_def_file

    def test_dependencies_changed_success(self, sandbox: dict[str, pathlib.Path]) -> None:
        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        old_version_cached = _load_cached_version(sandbox["VERSION_CACHE"])
        old_version_def_file = _load_built_version(sandbox["DEF_FILE"])

        _add_dependencies(sandbox["NON_BUILT"])
        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        assert _load_cached_version(sandbox["VERSION_CACHE"]) == old_version_cached - 0.1
        assert _load_built_version(sandbox["DEF_FILE"]) == old_version_def_file - 0.1

        _remove_dependencies(sandbox["NON_BUILT"])

    def test_major_version_changed_success(self, sandbox: dict[str, pathlib.Path]) -> None:
        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])

        old_version_cached = _load_cached_version(sandbox["VERSION_CACHE"])
        old_version_def_file = _load_built_version(sandbox["DEF_FILE"])

        pyproject_path = sandbox["NON_BUILT"] / "pyproject.toml"
        pyproject_data = toml.load(pyproject_path)
        pyproject_data["project"]["version"] = 3.0
        with pyproject_path.open("w") as f:
            toml.dump(pyproject_data, f)

        minor_version_bump(sandbox["BUILT"], sandbox["NON_BUILT"])
        assert _load_cached_version(sandbox["VERSION_CACHE"]) == old_version_cached + 1.0
        assert _load_built_version(sandbox["DEF_FILE"]) == old_version_def_file + 1.0

        pyproject_data = toml.load(pyproject_path)
        pyproject_data["project"]["version"] = "2.0"
        with pyproject_path.open("w") as f:
            toml.dump(pyproject_data, f)


def _load_cached_version(version_cache_path: pathlib.Path) -> float:
    with version_cache_path.open("r", encoding="utf-8") as f:
        versions_cache = yaml.safe_load(f)
        return versions_cache["version"]


def _load_built_version(def_file_path: pathlib.Path) -> float:
    with def_file_path.open("r", encoding="utf-8") as f:
        def_file = json.load(f)
        return def_file["Version"]


def _add_dependencies(non_built_integration_path: pathlib.Path) -> None:
    pyproject_path = non_built_integration_path / "pyproject.toml"
    pyproject_data = toml.load(pyproject_path)
    deps = pyproject_data["project"].setdefault("dependencies", [])
    deps.append("numpy==2.2.6")
    with pyproject_path.open("w") as f:
        toml.dump(pyproject_data, f)


def _remove_dependencies(non_built_integration_path: pathlib.Path) -> None:
    pyproject_path = non_built_integration_path / "pyproject.toml"
    pyproject_data = toml.load(pyproject_path)
    pyproject_data["project"]["dependencies"].pop()
    with pyproject_path.open("w") as f:
        toml.dump(pyproject_data, f)
