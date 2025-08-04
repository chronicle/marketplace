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

from typing import TYPE_CHECKING, Protocol

import rich
import typer

from mp.core.exceptions import FatalValidationError, NonFatalValidationError
from mp.validate.validation_results import ValidationResults, ValidationTypes

from .uv_lock_validation import UvLockValidation as UvLockValidation
from .version_bump_validation import VersionBumpValidation as VersionBumpValidation

if TYPE_CHECKING:
    import pathlib


class Validator(Protocol):
    validation_init_msg: str

    def run(self, validation_path: pathlib.Path) -> None:
        """Execute the validation process on the specified path.

        Args:
            validation_path: A `pathlib.Path` object pointing to the directory
                or file that needs to be validated.

        """


class PreBuildValidations:
    def __init__(self, integration_path: pathlib.Path) -> None:
        self.integration_path: pathlib.Path = integration_path
        self.results: ValidationResults = ValidationResults(
            integration_path.name, ValidationTypes.PRE_BUILD
        )

    def run_pre_build_validation(self) -> None:
        """Run all the pre-build validations.

        Raises:
            typer.Exit: If a `FatalValidationError` is encountered during any
                of the validation checks.

        """
        self.results.errors.append(
            "[bold green]Running pre build validation on"
            f" ---- {self.integration_path.name} ---- \n[/bold green]"
        )

        for validator in self._get_validation():
            try:
                self.results.errors.append(validator.validation_init_msg)
                validator.run(self.integration_path)

            except NonFatalValidationError as e:
                self.results.errors.append(f"[red]{e}\n[/red]")

            except FatalValidationError as error:
                rich.print(f"[bold red]{error}[/bold red]")
                raise typer.Exit(code=1) from error

        self.results.errors.append(
            "[bold green]Completed pre build validation on "
            f"---- {self.integration_path.name} ---- \n[/bold green]"
        )

        self.results.is_success = len(self.results.errors) == (len(self._get_validation()) + 2)

    @classmethod
    def _get_validation(cls) -> list[Validator]:
        return [UvLockValidation(), VersionBumpValidation()]
