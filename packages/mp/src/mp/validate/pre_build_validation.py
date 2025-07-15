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

import dataclasses
from typing import TYPE_CHECKING

import mp.core.file_utils
import mp.core.unix
from mp.core.exceptions.exceptions import NonFatalValidationError

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable


@dataclasses.dataclass(slots=True, frozen=True)
class PreBuildValidations:
    integration_path: pathlib.Path
    logs: list[str] = dataclasses.field(default_factory=list)

    @property
    def is_all_validation_passed(self) -> bool:
        """Check if all validations passed.

        Returns:
            bool: True if all validation passed, False otherwise.

        """
        return len(self.logs) == (len(self._get_validation_functions()) + 2)

    def run_pre_build_validation(self) -> None:
        """Run all the pre-build validations."""
        self.logs.append(
            "[bold green]Running pre build validation on "
            f"---- {self.integration_path.name} ---- \n[/bold green]"
        )

        for func in self._get_validation_functions():
            try:
                func()
            except NonFatalValidationError as e:
                self.logs.append(f"[red]{e!s}[/red]\n")

        self.logs.append(
            "[bold green]Completed pre build validation on "
            f"---- {self.integration_path.name} ---- \n[/bold green]"
        )

    def _get_validation_functions(self) -> list[Callable]:
        return [
            self._uv_lock_validation,
        ]

    def _uv_lock_validation(self) -> None:
        self.logs.append("[yellow]Running uv lock validation [/yellow]")
        if not mp.core.file_utils.is_built(self.integration_path):
            mp.core.unix.check_lock_file(self.integration_path)
