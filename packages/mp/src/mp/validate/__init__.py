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
import pathlib
from collections.abc import Callable
from typing import TYPE_CHECKING, Annotated, TypeAlias

import rich
import typer

import mp.core.config
import mp.core.file_utils
from mp.build_project.marketplace import Marketplace
from mp.core.custom_types import RepositoryType

from .pre_build_validation import PreBuildValidations
from .utils import Configurations, get_marketplace_paths_from_names

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from mp.core.config import RuntimeParams
    from mp.core.custom_types import Products

ValidationResults: TypeAlias = tuple[list[str], bool]
ValidationFn: TypeAlias = Callable[[pathlib.Path], ValidationResults]


__all__: list[str] = ["Configurations", "app"]
app: typer.Typer = typer.Typer()


@dataclasses.dataclass(slots=True, frozen=True)
class ValidateParams:
    repository: Iterable[RepositoryType]
    integrations: Iterable[str]
    groups: Iterable[str]
    only_pre_build: bool

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
        mutually_exclusive_options = [self.repository, self.integrations, self.groups]
        msg: str

        if not any(mutually_exclusive_options):
            msg = "At least one of --repository, --groups, or --integration must be used."
            raise typer.BadParameter(msg)

        if sum(map(bool, mutually_exclusive_options)) != 1:
            msg = "Only one of --repository, --groups, or --integration shall be used."
            raise typer.BadParameter(msg)


@app.command(help="Validate the marketplace")
def validate(  # noqa: PLR0913
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

    """
    run_params: RuntimeParams = mp.core.config.RuntimeParams(quiet, verbose)
    run_params.set_in_config()

    params: ValidateParams = ValidateParams(
        repository, integration, group, only_pre_build_validations
    )
    params.validate()

    commercial_mp: Marketplace = Marketplace(mp.core.file_utils.get_commercial_path())
    community_mp: Marketplace = Marketplace(mp.core.file_utils.get_community_path())

    run_configurations: Configurations = Configurations(
        only_pre_build_validations=only_pre_build_validations
    )

    if integration:
        rich.print(integration)
        _validate_integrations(
            get_marketplace_paths_from_names(integration, commercial_mp.path),
            commercial_mp,
            run_configurations,
        )
        _validate_integrations(
            get_marketplace_paths_from_names(integration, community_mp.path),
            community_mp,
            run_configurations,
        )

    elif group:
        _validate_groups(
            get_marketplace_paths_from_names(group, commercial_mp.path),
            commercial_mp,
            run_configurations,
        )
        _validate_groups(
            get_marketplace_paths_from_names(group, community_mp.path),
            community_mp,
            run_configurations,
        )

    elif repository:
        repos: set[RepositoryType] = set(repository)

        if RepositoryType.COMMERCIAL in repos:
            rich.print("Validating all integrations and groups in commercial repo...")
            _validate_repo(commercial_mp, run_configurations)
            rich.print("Done Commercial integrations validations.")

        if RepositoryType.COMMUNITY in repos:
            rich.print("Validating all integrations and groups in third party repo...")
            _validate_repo(community_mp, run_configurations)
            rich.print("Done third party integrations validations.")


def _validate_repo(marketplace: Marketplace, configurations: Configurations) -> None:
    products: Products[set[pathlib.Path]] = (
        mp.core.file_utils.get_integrations_and_groups_from_paths(marketplace.path)
    )
    rich.print(products.integrations)
    rich.print(products.groups)
    _validate_integrations(products.integrations, marketplace, configurations)
    _validate_groups(products.groups, marketplace, configurations)


def _validate_groups(
    groups: Iterable[pathlib.Path],
    marketplace: Marketplace,
    configurations: Configurations,
) -> None:
    """Validate a list of integration group names within a specific marketplace scope.

    Raises:
        typer.Exit: If any pre-build validation fails within the groups.

    """
    if groups:
        validations_passed: bool = _process_groups_for_validation(
            groups, _run_pre_build_validations
        )

        if not configurations.only_pre_build_validations:
            marketplace.build_groups(groups)

        if not validations_passed:
            raise typer.Exit(code=1)


def _process_groups_for_validation(
    groups: Iterable[pathlib.Path],
    validation_function: ValidationFn,
) -> bool:
    """Iterate through groups and perform pre-build validation on their integrations.

    Returns:
        bool: True if all validations passed, False otherwise.

    """
    all_validation_passed: bool = True
    for group_dir in groups:
        if group_dir.is_dir() and group_dir.exists():
            group_passed_validations = _run_validations(group_dir.iterdir(), validation_function)
            all_validation_passed = all_validation_passed and group_passed_validations

    return all_validation_passed


def _validate_integrations(
    integrations: Iterable[pathlib.Path],
    marketplace: Marketplace,
    configurations: Configurations,
) -> None:
    """Validate a list of integration names within a specific marketplace scope.

    Raises:
        typer.Exit: If any pre-build validation fails.

    """
    if integrations:
        validations_passed: bool = _run_validations(integrations, _run_pre_build_validations)

        if not configurations.only_pre_build_validations:
            marketplace.build_integrations(integrations)

        if not validations_passed:
            raise typer.Exit(code=1)


def _run_validations(
    integration: Iterable[pathlib.Path], validation_function: ValidationFn
) -> bool:
    """Execute pre-build validation checks on a list of integration paths.

    Returns:
        bool: True if all validations passed for the given paths, False otherwise.

    """
    paths: Iterator[pathlib.Path] = (
        p for p in integration if p.exists() and mp.core.file_utils.is_integration(p)
    )
    all_validation_passed: bool = True

    rich.print("[bold green]Starting pre-build validations [bold green]\n")

    processes: int = mp.core.config.get_processes_number()
    with multiprocessing.Pool(processes=processes) as pool:
        results = pool.imap_unordered(validation_function, paths)
        for msg_list, is_all_validation_passed in results:
            if not is_all_validation_passed:
                all_validation_passed = False
                _display_logs(msg_list)

    rich.print("[bold green]Completed pre-build validations [bold green]")
    return all_validation_passed


def _run_pre_build_validations(integration_path: pathlib.Path) -> ValidationResults:
    validation_object: PreBuildValidations = PreBuildValidations(integration_path)
    validation_object.run_pre_build_validation()
    return validation_object.logs, validation_object.is_all_validation_passed


def _display_logs(logs: list[str]) -> None:
    for log in logs:
        rich.print(log)
