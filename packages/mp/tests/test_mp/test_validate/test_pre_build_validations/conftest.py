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
from collections.abc import Iterator

import pytest


@pytest.fixture
def temp_integration(mock_get_marketplace_path: str) -> Iterator[pathlib.Path]:
    """Create a temporary integration directory with mock files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        test_file_dir = pathlib.Path(__file__).parent
        mock_path = (
            test_file_dir.parent.parent / "mock_marketplace" / "third_party" / "mock_integration"
        )
        shutil.copytree(mock_path.resolve(), temp_path / "mock_integration")
        yield temp_path / "mock_integration"
