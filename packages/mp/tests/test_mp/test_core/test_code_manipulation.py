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

import pytest

import mp.core.code_manipulation
from mp.core.constants import COMMON_SCRIPTS_DIR, CORE_SCRIPTS_DIR, SDK_PACKAGE_NAME


@pytest.mark.parametrize(
    ("original_import", "expected_restructured_import"),
    [
        (
            f"from ..{CORE_SCRIPTS_DIR}.module import something as s",
            "from module import something as s",
        ),
        (
            f"from ..{CORE_SCRIPTS_DIR} import another_thing, yet_another as y",
            "import another_thing, yet_another as y",
        ),
        (
            f"from {CORE_SCRIPTS_DIR} import another_thing, yet_another as y",
            "import another_thing, yet_another as y",
        ),
        (
            f"from ...{COMMON_SCRIPTS_DIR}.module.sub.a.b.c.d.e import something as s",
            "from e import something as s",
        ),
        (
            f"from ...{COMMON_SCRIPTS_DIR} import another_thing as at, yet_another",
            "import another_thing as at, yet_another",
        ),
        (
            f"from {COMMON_SCRIPTS_DIR} import another_thing as at, yet_another",
            "import another_thing as at, yet_another",
        ),
        (
            f"from ...{SDK_PACKAGE_NAME}.module.sub.a.b.c.d.e import something as s",
            "from e import something as s",
        ),
        (
            f"from ...{SDK_PACKAGE_NAME} import another_thing as at, yet_another",
            "import another_thing as at, yet_another",
        ),
        (
            f"from {SDK_PACKAGE_NAME} import another_thing as at, yet_another",
            "import another_thing as at, yet_another",
        ),
        (
            "from . import utils, constants as c",
            "import utils, constants as c",
        ),
        (
            "from .. import utils, constants as c",
            "import utils, constants as c",
        ),
        (
            "from .data_models import Integration as I",
            "from data_models import Integration as I",
        ),
        (
            "from .......data_models import Integration as I",
            "from data_models import Integration as I",
        ),
        (
            f"from .{CORE_SCRIPTS_DIR}.{COMMON_SCRIPTS_DIR} import authentication as a",
            f"from {COMMON_SCRIPTS_DIR} import authentication as a",
        ),
        (
            f"from .{CORE_SCRIPTS_DIR}.{COMMON_SCRIPTS_DIR}.module import authentication as a",
            "from module import authentication as a",
        ),
        (
            f"from .{COMMON_SCRIPTS_DIR}.something import authentication as a",
            "from something import authentication as a",
        ),
        (
            f"from .{COMMON_SCRIPTS_DIR}.{CORE_SCRIPTS_DIR} import authentication as a",
            f"from {CORE_SCRIPTS_DIR} import authentication as a",
        ),
        (
            f"from .{COMMON_SCRIPTS_DIR}.{CORE_SCRIPTS_DIR}.module import authentication as a",
            "from module import authentication as a",
        ),
        (
            "from ..another_module import another_thing",
            "from another_module import another_thing",
        ),
        (
            "from ..another_package.sub_package.module import another_thing",
            "from another_package.sub_package.module import another_thing",
        ),
        (
            "import os",
            "import os",
        ),
        (
            "import pathlib.Path",
            "import pathlib.Path",
        ),
    ],
)
def test_other_imports_are_not_modified(
    original_import: str,
    expected_restructured_import: str,
) -> None:
    modified_code: str = mp.core.code_manipulation.restructure_script_imports(
        original_import,
    )
    assert modified_code == expected_restructured_import
    compile(modified_code, filename="test_import_errors", mode="exec")
