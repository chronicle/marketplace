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

import shutil
import unittest.mock
from typing import TYPE_CHECKING, Any

import pytest

import mp.build_project.marketplace
import mp.core.constants
import test_mp.common

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable

    from mp.build_project.marketplace import Marketplace


def test_build_half_built_integration(
    tmp_path: pathlib.Path,
    half_built_integration: pathlib.Path,
    mock_get_marketplace_path: str,
    assert_build_integration: Callable[[pathlib.Path], None],
) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        assert_build_integration(half_built_integration)


def test_build_non_built_integration(
    tmp_path: pathlib.Path,
    non_built_integration: pathlib.Path,
    mock_get_marketplace_path: str,
    assert_build_integration: Callable[[pathlib.Path], None],
) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        assert_build_integration(non_built_integration)


def test_build_built_integration(
    tmp_path: pathlib.Path,
    built_integration: pathlib.Path,
    mock_get_marketplace_path: str,
    assert_build_integration: Callable[[pathlib.Path], None],
) -> None:
    with unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path):
        assert_build_integration(built_integration)


def test_non_existing_integration_raises_file_not_found_error(
    tmp_path: pathlib.Path,
    mock_get_marketplace_path: str,
    assert_build_integration: Callable[[pathlib.Path], None],
) -> None:
    with (
        unittest.mock.patch(mock_get_marketplace_path, return_value=tmp_path),
        pytest.raises(FileNotFoundError, match=r"Invalid integration .*"),
    ):
        assert_build_integration(tmp_path / "fake_integration")


@pytest.fixture
def assert_build_integration(
    tmp_path: pathlib.Path,
    built_integration: pathlib.Path,
) -> Callable[[pathlib.Path], None]:
    def wrapper(integration_path: pathlib.Path) -> None:
        commercial: pathlib.Path = tmp_path / built_integration.parent.name
        shutil.copytree(integration_path.parent, commercial)
        integration: pathlib.Path = commercial / built_integration.name

        marketplace: Marketplace = mp.build_project.marketplace.Marketplace(commercial)
        marketplace.build_integration(integration)

        out_integration: pathlib.Path = marketplace.out_path / integration.name
        expected_file_names: set[str] = {
            p.name for p in built_integration.rglob("*.*") if ".venv" not in p.parts
        }
        actual_file_names: set[str] = {
            p.name for p in out_integration.rglob("*.*") if ".venv" not in p.parts
        }
        assert actual_file_names == expected_file_names

        actual_file_names, expected_file_names = test_mp.common.compare_dependencies(
            expected=built_integration / mp.core.constants.OUT_DEPENDENCIES_DIR,
            actual=out_integration / mp.core.constants.OUT_DEPENDENCIES_DIR,
        )
        assert actual_file_names == expected_file_names

        actual: dict[str, Any]
        expected: dict[str, Any]
        actual, expected = test_mp.common.get_json_content(
            expected=built_integration / mp.core.constants.RN_JSON_FILE,
            actual=out_integration / mp.core.constants.RN_JSON_FILE,
        )
        assert actual == expected

        actual, expected = test_mp.common.get_json_content(
            expected=(
                built_integration
                / mp.core.constants.INTEGRATION_DEF_FILE.format(built_integration.name)
            ),
            actual=(
                out_integration
                / mp.core.constants.INTEGRATION_DEF_FILE.format(built_integration.name)
            ),
        )
        assert actual == expected

        actual, expected = test_mp.common.get_json_content(
            expected=(
                built_integration
                / mp.core.constants.INTEGRATION_FULL_DETAILS_FILE.format(
                    built_integration.name,
                )
            ),
            actual=(
                out_integration
                / mp.core.constants.INTEGRATION_FULL_DETAILS_FILE.format(
                    built_integration.name,
                )
            ),
        )
        assert actual == expected

        actual, expected = test_mp.common.get_json_content(
            expected=(
                built_integration
                / mp.core.constants.OUT_MAPPING_RULES_DIR
                / mp.core.constants.OUT_MAPPING_RULES_FILE
            ),
            actual=(
                out_integration
                / mp.core.constants.OUT_MAPPING_RULES_DIR
                / mp.core.constants.OUT_MAPPING_RULES_FILE
            ),
        )
        assert actual == expected

        actual, expected = test_mp.common.get_json_content(
            expected=(
                built_integration
                / mp.core.constants.OUT_CUSTOM_FAMILIES_DIR
                / mp.core.constants.OUT_CUSTOM_FAMILIES_FILE
            ),
            actual=(
                out_integration
                / mp.core.constants.OUT_CUSTOM_FAMILIES_DIR
                / mp.core.constants.OUT_CUSTOM_FAMILIES_FILE
            ),
        )
        assert actual == expected

    return wrapper
