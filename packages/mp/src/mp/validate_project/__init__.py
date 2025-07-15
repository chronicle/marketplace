"""Package for validate integration projects.

This package provides the 'validate' CLI command for processing integration
repositories, groups, or individual integrations and run pre build and post build validations.
"""

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
import multiprocessing
from typing import TYPE_CHECKING, Annotated

import rich
import typer

import mp.core.config
import mp.core.file_utils
from mp.build_project.marketplace import Marketplace
from mp.build_project.post_build.duplicate_integrations import (
    raise_errors_for_duplicate_integrations,
)
from mp.core.config import RuntimeParams
from mp.core.custom_types import RepositoryType

from .pre_build_validation import PreBuildValidations

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterable, Iterator

    from mp.core.custom_types import Products


__all__: list[str] = [
    "Marketplace",
    "PreBuildValidations",
    "RuntimeParams",
    "app",
    "raise_errors_for_duplicate_integrations",
]
app: typer.Typer = typer.Typer()


@dataclasses.dataclass(slots=True, frozen=True)
class BuildParams:
    repository: Iterable[RepositoryType]
    integrations: Iterable[str]
    groups: Iterable[str]
    only_pre_build: bool | None

    def validate(self) -> None:
        """Validate the parameters.

        Validates the provided parameters
        to ensure proper usage of mutually exclusive
        options and constraints.
        Handles error messages and raises exceptions if validation fails.

        Raises:
            typer.BadParameter:
                If none of the required options (--repository, --groups, or
                --integration) are provided.
            typer.BadParameter:
                If more than one of the options (--repository, --groups,
                or --integration) is used at the same time.

        """
        params: list[Iterable[str] | Iterable[RepositoryType]] = self._as_list()
        msg: str
        if not any(params):
            msg = "At least one of --repository, --groups, or --integration must be used."
            raise typer.BadParameter(msg)

        if sum(map(bool, params)) != 1:
            msg = "Only one of --repository, --groups, or --integration shall be used."
            raise typer.BadParameter(msg)

    def _as_list(self) -> list[Iterable[RepositoryType] | Iterable[str]]:
        return [self.repository, self.integrations, self.groups]


@app.command(name="validate", help="Validate the marketplace")
def validate_command(  # noqa: PLR0913
    repository: Annotated[
        list[RepositoryType],
        typer.Option(
            help="Run validation on all integrations in specified integration repositories",
            default_factory=list,
        ),
    ],
    integration: Annotated[
        list[str],
        typer.Option(
            help="Run validation on a specified integrations.",
            default_factory=list,
        ),
    ],
    group: Annotated[
        list[str],
        typer.Option(
            help="Run validation on all integrations belonging to a specified integration group.",
            default_factory=list,
        ),
    ],
    *,
    only_pre_build_validations: Annotated[
        bool,
        typer.Option(
            help=(
                "Execute only pre-build validation "
                "checks on the integrations, skipping the full build process."
            ),
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            help="Suppress most logging output during runtime, showing only essential information.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            help="Enable verbose logging output during runtime for detailed debugging information.",
        ),
    ] = False,
) -> None:
    """Run the mp validate command.
    Validate integrations within the marketplace based on specified criteria.

    Args:
        repository: A list of repository types on which to run validation.
                    Validation will be performed on all integrations found
                    within these repositories.
        integration: A list of specific integration to validate.
        group: A list of integration groups. Validation will apply to all
               integrations associated with these groups.
        only_pre_build_validations: If set to True, only pre-build validation checks are
                        performed.
        quiet: quiet log options
        verbose: Verbose log options

    """  # noqa: D205
    run_params: RuntimeParams = mp.core.config.RuntimeParams(quiet, verbose)
    run_params.set_in_config()

    params: BuildParams = BuildParams(repository, integration, group, only_pre_build_validations)
    params.validate()

    commercial_mp: Marketplace = Marketplace(mp.core.file_utils.get_commercial_path())
    community_mp: Marketplace = Marketplace(mp.core.file_utils.get_community_path())

    if integration:
        _validate_integrations(
            set(integration), commercial_mp, only_pre_build_validations=only_pre_build_validations
        )
        _validate_integrations(
            set(integration), community_mp, only_pre_build_validations=only_pre_build_validations
        )

    elif group:
        _validate_groups(
            set(group), commercial_mp, only_pre_build_validations=only_pre_build_validations
        )
        _validate_groups(
            set(group), community_mp, only_pre_build_validations=only_pre_build_validations
        )

    elif repository:
        repos: set[RepositoryType] = set(repository)
        if RepositoryType.COMMERCIAL in repos:
            rich.print("Validating all integrations and groups in commercial repo...")
            _validate_repo(commercial_mp, only_pre_build_validations=only_pre_build_validations)
            rich.print("Done Commercial integrations validations.")

        if RepositoryType.COMMUNITY in repos:
            rich.print("Validating all integrations and groups in third party repo...")
            _validate_repo(community_mp, only_pre_build_validations=only_pre_build_validations)
            rich.print("Done third party integrations validations.")


def _validate_repo(marketplace: Marketplace, *, only_pre_build_validations: bool) -> None:
    products: Products[set[pathlib.Path]] = (
        mp.core.file_utils.get_integrations_and_groups_from_paths(marketplace.path)
    )

    _validate_integrations(
        set(products.integrations),
        marketplace,
        only_pre_build_validations=only_pre_build_validations,
        pass_integration_by_path=True,
    )
    _validate_groups(
        set(products.groups),
        marketplace,
        only_pre_build_validations=only_pre_build_validations,
        pass_group_by_path=True,
    )


def _validate_integrations(
    integrations: Iterable[str] | Iterable[pathlib.Path],
    marketplace_: Marketplace,
    *,
    only_pre_build_validations: bool,
    pass_integration_by_path: bool = False,
) -> None:
    """Validate a list of integration names within a specific marketplace scope.

    Raises:
        typer.Exit: If any pre-build validation fails.

    """
    if not pass_integration_by_path:
        valid_integrations_paths: set[pathlib.Path] = _get_marketplace_paths_from_names(
            integrations,
            marketplace_.path,
        )
    else:
        valid_integrations_paths: set[pathlib.Path] = integrations

    if valid_integrations_paths:
        validations_passed: bool = _pre_build_validation(valid_integrations_paths)

        if not only_pre_build_validations:
            marketplace_.build_integrations(valid_integrations_paths)
            # Place holder for post build validations

        if not validations_passed:
            raise typer.Exit(code=1)


def _validate_groups(
    groups: Iterable[str] | Iterable[pathlib.Path],
    marketplace_: Marketplace,
    *,
    only_pre_build_validations: bool,
    pass_group_by_path: bool = False,
) -> None:
    """Validate a list of integration group names within a specific marketplace scope.

    Raises:
        typer.Exit: If any pre-build validation fails within the groups.

    """
    if not pass_group_by_path:
        valid_groups_paths: set[pathlib.Path] = _get_marketplace_paths_from_names(
            names=groups,
            marketplace_path=marketplace_.path,
        )
    else:
        valid_groups_paths: set[pathlib.Path] = set(groups)

    if valid_groups_paths:
        validations_passed: bool = _process_groups_for_validation(valid_groups_paths)

        if not only_pre_build_validations:
            marketplace_.build_groups(valid_groups_paths)
            # Place holder for post build validations

        if not validations_passed:
            raise typer.Exit(code=1)


def _process_groups_for_validation(groups: Iterable[pathlib.Path]) -> bool:
    """Iterate through groups and perform pre-build validation on their integrations.

    Returns:
        bool: True if all validations passed, False otherwise.

    """
    all_validation_passed: bool = True
    for group_dir in groups:
        if group_dir.is_dir() and group_dir.exists():
            group_passed_validations = _pre_build_validation(group_dir.iterdir())
            all_validation_passed = all_validation_passed and group_passed_validations

    return all_validation_passed


def _pre_build_validation(integration_paths: Iterable[pathlib.Path]) -> bool:
    """Execute pre-build validation checks on a list of integration paths.

    Returns:
        bool: True if all validations passed for the given paths, False otherwise.

    """
    paths: Iterator[pathlib.Path] = (
        p for p in integration_paths if p.exists() and mp.core.file_utils.is_integration(p)
    )
    all_validation_passed: bool = True

    processes: int = mp.core.config.get_processes_number()
    logs_array: list[list[str]] = []
    with multiprocessing.Pool(processes=processes) as pool:
        results = pool.imap_unordered(_run_pre_build_validations, paths)
        for msg_list, is_all_validation_passed in results:
            if not is_all_validation_passed:
                all_validation_passed = False
                logs_array.append(msg_list.copy())

    for logger in logs_array:
        for msg in logger:
            rich.print(msg)

    return all_validation_passed


def _run_pre_build_validations(integration_path: pathlib.Path) -> tuple[list[str], bool]:
    validation_object: PreBuildValidations = PreBuildValidations(integration_path)
    validation_object.run_pre_build_validation()
    return validation_object.get_logs(), validation_object.is_all_validation_passed()


def _post_build_validation(integration_paths: Iterable[pathlib.Path]) -> None:
    pass


def run_post_build_validation(integration_path: pathlib.Path) -> None:
    pass


def _get_marketplace_paths_from_names(
    names: Iterable[str] | Iterable[pathlib.Path],
    marketplace_path: pathlib.Path,
) -> set[pathlib.Path]:
    result: set[pathlib.Path] = set()
    for n in names:
        p = marketplace_path / n
        if p.exists():
            result.add(p)
        else:
            rich.print(
                "[yellow] the integration: "
                f"{n} has not been found in {marketplace_path.name} [yellow]"
            )
    return result
