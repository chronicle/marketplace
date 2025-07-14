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


import dataclasses
import pathlib
from collections.abc import Callable

from mp.common.exceptions import NonFatalExceptionError
from mp.core.file_utils import is_built
from mp.core.unix import check_lock_file


@dataclasses.dataclass(slots=True, frozen=True)
class PreBuildValidations:
    integration_path: pathlib.Path
    logs: list[str] = dataclasses.field(default_factory=list)

    def get_logs(self) -> list[str]:
        """Return the log object that stores all the logs inside it.

        Returns:
            list[str]: A list containing all the logs.

        """
        return self.logs

    def is_all_validation_passed(self) -> bool:
        """Check if all validation has passed.

        Returns:
            bool: True if all validation passed, False otherwise.

        """
        return len(self.logs) == (len(self._get_validation_functions()) + 2)

    def run_pre_build_validation(self) -> None:
        """Run all the pre-build validations."""
        self.logs.append(
            "[bold green]Running pre build validation on "
            f"---- {self.integration_path.name} ---- [/bold green]"
        )

        for func in self._get_validation_functions():
            try:
                func()
            except NonFatalExceptionError as e:
                self.logs.append(f"[red]{e.message}[/red]")

        self.logs.append(
            "[bold green]Completed pre build validation on "
            f"---- {self.integration_path.name} ---- [/bold green]"
        )

    def _get_validation_functions(self) -> list[Callable]:
        return [
            self._uv_lock_validation,
        ]

    def _uv_lock_validation(self) -> None:
        self.logs.append("[yellow]Running uv lock validation [/yellow]")
        if not is_built(self.integration_path):
            check_lock_file(self.integration_path)
