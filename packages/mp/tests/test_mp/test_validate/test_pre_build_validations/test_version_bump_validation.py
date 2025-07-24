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

import pathlib
import shutil
import tempfile
import unittest.mock

import pytest

import mp.core.unix
from mp.core.exceptions import NonFatalValidationError
from mp.validate.pre_build_validation.version_bump_validation import (
    _create_data_for_version_bump_validation,  # noqa: PLC2701
    _version_bump_validation_run_checks,  # noqa: PLC2701
)

PYPROJECT_TOML_TEMPLATE = """[project]
name = "mock_integration"
version = "{version}"
description = "Mock Integration description"
requires-python = ">=3.11"
dependencies = [
    "requests==2.32.4",
]"""

OLD_RN_CONTENT = """# Copyright header
-   deprecated: true
    description: New Integration Added - Mock Integration.
    integration_version: 1.0
    item_name: Connector Name
    item_type: Connector
    new: true
    regressive: false
    removed: false
    ticket_number: some ticket"""

NEW_RN_ENTRY_TEMPLATE = """
-   deprecated: {deprecated}
    description: {description}
    integration_version: {version}
    item_name: {item_name}
    item_type: {item_type}
    new: {new}
    regressive: false
    removed: false
    ticket_number: {ticket}"""

NEW_INTEGRATION_RN_TEMPLATE = """# Copyright header
-   deprecated: {deprecated}
    description: {description}
    integration_version: {version}
    item_name: {item_name}
    item_type: {item_type}
    new: {new}
    regressive: false
    removed: false
    ticket_number: {ticket}"""


def _setup_test_files(
    temp_integration: pathlib.Path, new_toml_content: str, new_rn_content: str
) -> tuple[pathlib.Path, pathlib.Path]:
    """Write content to mock integration files and return their paths."""
    rn_path = temp_integration / "release_notes.yaml"
    toml_path = temp_integration / "pyproject.toml"
    toml_path.write_text(new_toml_content, encoding="utf-8")
    rn_path.write_text(new_rn_content, encoding="utf-8")
    return rn_path, toml_path


@pytest.fixture
def temp_integration() -> pathlib.Path:
    """Create a temporary integration directory with mock files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        test_file_dir = pathlib.Path(__file__).parent
        mock_path = (
            test_file_dir / ".." / ".." / "mock_marketplace" / "third_party" / "mock_integration"
        )
        mock_path = mock_path.resolve()
        shutil.copytree(mock_path, temp_path / "mock_integration")
        yield temp_path / "mock_integration"


class TestVersionBumpValidationFlow:
    def test_valid_existing_integration_version_bump(self, temp_integration: pathlib.Path) -> None:
        """Test complete flow for existing integration with valid version bump."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="2.0")
        new_rn_entry = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Version 2.0 update",
            version="2.0",
            item_name="Integration Name",
            item_type="Integration",
            new="false",
            ticket="UPDATE-123",
        )
        new_rn_content = OLD_RN_CONTENT + new_rn_entry
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 2.0
            assert existing_files["rn"]["old"].version == 1.0
            assert existing_files["rn"]["new"][0].version == 2.0

            _version_bump_validation_run_checks(existing_files, new_files)

    def test_invalid_existing_integration_version_bump(
        self, temp_integration: pathlib.Path
    ) -> None:
        """Test complete flow for existing integration with invalid version bump."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="3.0")
        new_rn_entry = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Version 3.0 update",
            version="3.0",
            item_name="Integration Name",
            item_type="Integration",
            new="false",
            ticket="UPDATE-456",
        )
        new_rn_content = OLD_RN_CONTENT + new_rn_entry
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 3.0

            with pytest.raises(
                NonFatalValidationError, match=r"must be incremented by exactly 1\.0"
            ):
                _version_bump_validation_run_checks(existing_files, new_files)

    def test_invalid_existing_integration_version_bump_float(
        self, temp_integration: pathlib.Path
    ) -> None:
        """Test complete flow for existing integration with invalid version bump."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.5")
        new_rn_entry = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Version 1.5 update",
            version="1.5",
            item_name="Integration Name",
            item_type="Integration",
            new="false",
            ticket="UPDATE-456",
        )
        new_rn_content = OLD_RN_CONTENT + new_rn_entry
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 1.5
            assert existing_files["rn"]["old"].version == 1.0
            assert existing_files["rn"]["new"][0].version == 1.5

            with pytest.raises(
                NonFatalValidationError, match=r"must be incremented by exactly 1\.0"
            ):
                _version_bump_validation_run_checks(existing_files, new_files)

    def test_mismatched_release_note_version(self, temp_integration: pathlib.Path) -> None:
        """Test complete flow for existing integration with mismatched release note version."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="2.0")
        new_rn_entry = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Version update",
            version="4.0",
            item_name="Integration Name",
            item_type="Integration",
            new="false",
            ticket="UPDATE-789",
        )
        new_rn_content = OLD_RN_CONTENT + new_rn_entry
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 2.0
            assert existing_files["rn"]["old"].version == 1.0
            assert existing_files["rn"]["new"][0].version == 4.0

            with pytest.raises(NonFatalValidationError, match="release note's version must match"):
                _version_bump_validation_run_checks(existing_files, new_files)

    def test_valid_new_integration(self, temp_integration: pathlib.Path) -> None:
        """Test complete flow for new integration with valid initial version."""
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_rn_content = NEW_INTEGRATION_RN_TEMPLATE.format(
            deprecated="false",
            description="New Integration Added - Mock Integration.",
            version="1.0",
            item_name="Integration Name",
            item_type="Integration",
            new="true",
            ticket="NEW-123",
        )
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = mp.core.unix.NonFatalCommandError(
                "File not found on main branch"
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert not existing_files["toml"].get("old")
            assert new_files["toml"].project.version == 1.0
            assert len(new_files["rn"]) == 1
            assert new_files["rn"][0].version == 1.0

            _version_bump_validation_run_checks(existing_files, new_files)

    def test_invalid_new_integration_wrong_version(self, temp_integration: pathlib.Path) -> None:
        """Test complete flow for new integration with invalid initial version."""
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="2.0")
        new_rn_content = NEW_INTEGRATION_RN_TEMPLATE.format(
            deprecated="false",
            description="New Integration Added - Mock Integration.",
            version="2.0",
            item_name="Integration Name",
            item_type="Integration",
            new="true",
            ticket="NEW-456",
        )
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = mp.core.unix.NonFatalCommandError(
                "File not found on main branch"
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert new_files["toml"].project.version == 2.0
            assert new_files["rn"][0].version == 2.0

            with pytest.raises(NonFatalValidationError, match=r"must be initialize to 1\.0"):
                _version_bump_validation_run_checks(existing_files, new_files)

    def test_invalid_new_integration_mismatched_rn_version(
        self, temp_integration: pathlib.Path
    ) -> None:
        """Test complete flow for new integration with mismatched release note version."""
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_rn_content = NEW_INTEGRATION_RN_TEMPLATE.format(
            deprecated="false",
            description="New Integration Added - Mock Integration.",
            version="2.0",
            item_name="Integration Name",
            item_type="Integration",
            new="true",
            ticket="NEW-789",
        )
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = mp.core.unix.NonFatalCommandError(
                "File not found on main branch"
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert new_files["toml"].project.version == 1.0
            assert new_files["rn"][0].version == 2.0

            with pytest.raises(NonFatalValidationError, match=r"must be initialize to 1\.0"):
                _version_bump_validation_run_checks(existing_files, new_files)

    def test_integration_with_multiple_new_release_notes(
        self, temp_integration: pathlib.Path
    ) -> None:
        """Test complete flow for existing integration with multiple new release notes."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="2.0")
        rn_entry_a = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Feature A added",
            version="2.0",
            item_name="Action A",
            item_type="Action",
            new="true",
            ticket="FEAT-A",
        )
        rn_entry_b = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Feature B added",
            version="2.0",
            item_name="Action B",
            item_type="Action",
            new="true",
            ticket="FEAT-B",
        )
        new_rn_content = OLD_RN_CONTENT + rn_entry_a + rn_entry_b
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 2.0
            new_notes = existing_files["rn"]["new"]
            assert new_notes is not None
            assert len(new_notes) == 2
            assert all(note.version == 2.0 for note in new_notes)

            _version_bump_validation_run_checks(existing_files, new_files)

    def test_integration_with_multiple_invalid_new_release_notes(
        self, temp_integration: pathlib.Path
    ) -> None:
        """Test complete flow for existing integration with multiple new invalid release notes."""
        old_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="1.0")
        new_toml_content = PYPROJECT_TOML_TEMPLATE.format(version="2.0")
        rn_entry_a = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Feature A added",
            version="2.0",
            item_name="Action A",
            item_type="Action",
            new="true",
            ticket="FEAT-A",
        )
        rn_entry_b = NEW_RN_ENTRY_TEMPLATE.format(
            deprecated="false",
            description="Feature B added",
            version="4.0",
            item_name="Action B",
            item_type="Action",
            new="true",
            ticket="FEAT-B",
        )
        new_rn_content = OLD_RN_CONTENT + rn_entry_a + rn_entry_b
        rn_path, toml_path = _setup_test_files(temp_integration, new_toml_content, new_rn_content)

        with unittest.mock.patch("mp.core.unix.get_file_content_from_main_branch") as mock_git:
            mock_git.side_effect = lambda path: (
                old_toml_content if path.name == "pyproject.toml" else OLD_RN_CONTENT
            )
            existing_files, new_files = _create_data_for_version_bump_validation(rn_path, toml_path)

            assert existing_files["toml"]["old"].project.version == 1.0
            assert existing_files["toml"]["new"].project.version == 2.0
            new_notes = existing_files["rn"]["new"]
            assert new_notes is not None
            assert len(new_notes) == 2

            with pytest.raises(NonFatalValidationError, match=r"The release note's version must "):
                _version_bump_validation_run_checks(existing_files, new_files)
