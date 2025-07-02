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

import unittest.mock
from typing import TYPE_CHECKING

import mp.core.constants
import mp.core.file_utils

if TYPE_CHECKING:
    import pathlib

    from mp.core.custom_types import Products


def test_discover_managers_built(tmp_path: pathlib.Path) -> None:
    (tmp_path / mp.core.constants.INTEGRATION_DEF_FILE.format(tmp_path.name)).touch()
    (tmp_path / "manager0.py").touch()
    (tmp_path / "manager1.json").touch()

    out_managers_dir: pathlib.Path = tmp_path / mp.core.constants.OUT_MANAGERS_SCRIPTS_DIR
    out_managers_dir.mkdir(parents=True)
    (out_managers_dir / "manager1.py").touch()
    (out_managers_dir / "manager2.py").touch()

    assert mp.core.file_utils.is_built(tmp_path)
    managers: list[str] = mp.core.file_utils.discover_core_modules(tmp_path)
    assert set(managers) == {"manager1", "manager2"}


def test_discover_managers_not_built(tmp_path: pathlib.Path) -> None:
    (tmp_path / mp.core.constants.PROJECT_FILE).touch()

    common_scripts_dir: pathlib.Path = tmp_path / mp.core.constants.CORE_SCRIPTS_DIR
    common_scripts_dir.mkdir(parents=True)
    (common_scripts_dir / "manager1.py").touch()
    (common_scripts_dir / "manager2.py").touch()

    assert not mp.core.file_utils.is_built(tmp_path)
    managers = mp.core.file_utils.discover_core_modules(tmp_path)
    assert set(managers) == {"manager1", "manager2"}


def test_get_integrations_and_groups_from_paths(tmp_path: pathlib.Path) -> None:
    commercial_dir: pathlib.Path = tmp_path / mp.core.constants.COMMERCIAL_DIR_NAME
    commercial_dir.mkdir()
    (commercial_dir / "integration1").mkdir()
    (commercial_dir / "integration1" / mp.core.constants.PROJECT_FILE).touch()
    (commercial_dir / "group1").mkdir()
    (commercial_dir / "group1" / "integration2").mkdir()
    (commercial_dir / "group1" / "integration2" / mp.core.constants.PROJECT_FILE).touch()

    community_dir: pathlib.Path = tmp_path / mp.core.constants.COMMUNITY_DIR_NAME
    community_dir.mkdir()
    (community_dir / "integration3").mkdir()
    (community_dir / "integration3" / mp.core.constants.PROJECT_FILE).touch()
    (community_dir / "group2").mkdir()
    (community_dir / "group2" / "integration4").mkdir()
    (community_dir / "group2" / "integration4" / mp.core.constants.PROJECT_FILE).touch()

    products: Products[set[pathlib.Path]] = (
        mp.core.file_utils.get_integrations_and_groups_from_paths(commercial_dir, community_dir)
    )

    assert products.integrations == {
        commercial_dir / "integration1",
        community_dir / "integration3",
    }
    assert products.groups == {commercial_dir / "group1", community_dir / "group2"}


def test_is_python_file(tmp_path: pathlib.Path) -> None:
    (tmp_path / "test.py").touch()
    (tmp_path / "test.txt").touch()

    assert mp.core.file_utils.is_python_file(tmp_path / "test.py")
    assert not mp.core.file_utils.is_python_file(tmp_path / "test.txt")
    assert not mp.core.file_utils.is_python_file(tmp_path / "not_exists")


def test_is_integration(tmp_path: pathlib.Path) -> None:
    commercial_dir: pathlib.Path = tmp_path / mp.core.constants.COMMERCIAL_DIR_NAME
    community_dir: pathlib.Path = tmp_path / mp.core.constants.COMMUNITY_DIR_NAME
    integration_dir_comm: pathlib.Path = community_dir / "integration"
    integration_dir_com: pathlib.Path = commercial_dir / "integration"

    commercial_dir.mkdir()
    community_dir.mkdir()
    integration_dir_comm.mkdir()
    integration_dir_com.mkdir()
    (integration_dir_comm / mp.core.constants.PROJECT_FILE).touch()
    (integration_dir_com / mp.core.constants.PROJECT_FILE).touch()

    assert mp.core.file_utils.is_integration(integration_dir_com)
    assert mp.core.file_utils.is_integration(integration_dir_comm)
    assert not mp.core.file_utils.is_integration(tmp_path)


def test_is_group(tmp_path: pathlib.Path) -> None:
    commercial_dir: pathlib.Path = tmp_path / mp.core.constants.COMMERCIAL_DIR_NAME
    community_dir: pathlib.Path = tmp_path / mp.core.constants.COMMUNITY_DIR_NAME
    commercial_dir.mkdir()
    community_dir.mkdir()

    group_dir_commercial: pathlib.Path = commercial_dir / "group"
    group_dir_community: pathlib.Path = community_dir / "group"
    group_dir_commercial.mkdir()
    group_dir_community.mkdir()

    (group_dir_community / "integration1").mkdir()
    (group_dir_community / "integration1" / mp.core.constants.PROJECT_FILE).touch()
    (group_dir_commercial / "integration2").mkdir()
    (group_dir_commercial / "integration2" / mp.core.constants.PROJECT_FILE).touch()

    assert mp.core.file_utils.is_group(group_dir_commercial)
    assert mp.core.file_utils.is_group(group_dir_community)
    assert not mp.core.file_utils.is_group(tmp_path)


def test_replace_file_content(tmp_path: pathlib.Path) -> None:
    test_file: pathlib.Path = tmp_path / "test.txt"
    test_file.write_text("original content", encoding="utf-8")

    def replace_fn(content: str) -> str:
        return content.replace("original", "new")

    mp.core.file_utils.replace_file_content(test_file, replace_fn)
    assert test_file.read_text(encoding="utf-8") == "new content"

    def replace_fn2(content: str) -> str:
        return content.replace("new content", "final content")

    mp.core.file_utils.replace_file_content(test_file, replace_fn2)
    assert test_file.read_text(encoding="utf-8") == "final content"


def test_remove_paths_if_exists_can_remove_files(
    tmp_path: pathlib.Path,
    mock_get_marketplace_path: str,
) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        test_file: pathlib.Path = tmp_path / "test.txt"
        test_file.touch()
        assert test_file.exists()

        mp.core.file_utils.remove_paths_if_exists(test_file)
        assert not test_file.exists()

        # Check if it fails when a file does not exist
        mp.core.file_utils.remove_paths_if_exists(test_file)
        assert not test_file.exists()


def test_remove_paths_if_exists_can_remove_dirs(
    tmp_path: pathlib.Path,
    mock_get_marketplace_path: str,
) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        test_subdir: pathlib.Path = tmp_path / "subdir"
        test_subdir.mkdir()
        assert test_subdir.exists()

        mp.core.file_utils.remove_paths_if_exists(test_subdir)
        assert not test_subdir.exists()

        # Check if it fails when a folder does not exist
        mp.core.file_utils.remove_paths_if_exists(test_subdir)
        assert not test_subdir.exists()


def test_is_built(tmp_path: pathlib.Path) -> None:
    integration_dir: pathlib.Path = tmp_path / "integration"
    integration_dir.mkdir()

    def_file_name: str = mp.core.constants.INTEGRATION_DEF_FILE.format(
        integration_dir.name,
    )
    (integration_dir / def_file_name).touch()
    assert mp.core.file_utils.is_built(integration_dir)

    (integration_dir / def_file_name).unlink()
    (integration_dir / mp.core.constants.PROJECT_FILE).touch()
    assert not mp.core.file_utils.is_built(integration_dir)
    assert not mp.core.file_utils.is_built(tmp_path)


def test_is_half_built(tmp_path: pathlib.Path) -> None:
    integration_dir: pathlib.Path = tmp_path / "integration"
    integration_dir.mkdir()

    def_file_name: str = mp.core.constants.INTEGRATION_DEF_FILE.format(
        integration_dir.name,
    )
    (integration_dir / mp.core.constants.PROJECT_FILE).touch()
    (integration_dir / def_file_name).touch()
    assert mp.core.file_utils.is_half_built(integration_dir)

    (integration_dir / def_file_name).unlink()
    assert not mp.core.file_utils.is_half_built(integration_dir)

    (integration_dir / mp.core.constants.PROJECT_FILE).unlink()
    (integration_dir / def_file_name).touch()
    assert not mp.core.file_utils.is_half_built(integration_dir)
    assert not mp.core.file_utils.is_half_built(tmp_path)


def test_remove_and_create_dir(tmp_path: pathlib.Path, mock_get_marketplace_path: str) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        test_dir: pathlib.Path = tmp_path / "test"
        test_dir.mkdir()
        assert test_dir.exists()

        new_file: pathlib.Path = test_dir / "file.txt"
        new_file.touch()
        assert new_file.exists()

        mp.core.file_utils.recreate_dir(test_dir)

        assert test_dir.exists()
        assert not new_file.exists()
