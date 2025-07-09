"""Package for building and deconstructing integration projects.

This package provides the `build` CLI command for processing integration
repositories, groups, or individual integrations. It handles both building
integrations into a deployable format and deconstructing built integrations
back into their source structure. The package also includes modules for
managing the marketplace JSON, restructuring integration components (metadata,
scripts, code, dependencies), and defining an interface for restructurable
components.
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
from typing import TYPE_CHECKING, Annotated

import rich
import typer

import mp.core.config
import mp.core.file_utils
from mp.core.custom_types import RepositoryType

from .marketplace import Marketplace
from .post_build.duplicate_integrations import raise_errors_for_duplicate_integrations

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterable, Sequence

    from mp.core.config import RuntimeParams


__all__: list[str] = ["app"]
app: typer.Typer = typer.Typer()


@dataclasses.dataclass(slots=True, frozen=True)
class BuildParams:
    repository: Iterable[RepositoryType]
    integrations: Iterable[str]
    groups: Iterable[str]
    deconstruct: bool

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
            typer.BadParameter:
                If the --deconstruct option is used with any option
                other than --integration.

        """
        params: list[Iterable[str] | Iterable[RepositoryType]] = self._as_list()
        msg: str
        if not any(params):
            msg = "At least one of --repository, --groups, or --integration must be used."
            raise typer.BadParameter(msg)

        if sum(map(bool, params)) != 1:
            msg = "Only one of --repository, --groups, or --integration shall be used."
            raise typer.BadParameter(msg)

        if self.deconstruct and (self.groups or self.repository):
            msg = "--deconstruct works only with --integration."
            raise typer.BadParameter(msg)

    def _as_list(self) -> list[Iterable[RepositoryType] | Iterable[str]]:
        return [self.repository, self.integrations, self.groups]


@app.command(name="build", help="Build the marketplace")
def build(  # noqa: PLR0913
    repository: Annotated[
        list[RepositoryType],
        typer.Option(
            help="Build all integrations in specified integration repositories",
            default_factory=list,
        ),
    ],
    integration: Annotated[
        list[str],
        typer.Option(
            help="Build a specified integration",
            default_factory=list,
        ),
    ],
    group: Annotated[
        list[str],
        typer.Option(
            help="Build all integrations of a specified integration group",
            default_factory=list,
        ),
    ],
    *,
    deconstruct: Annotated[
        bool,
        typer.Option(
            help=(
                "Deconstruct built integrations instead of building them."
                " Does work only with --integration."
            ),
        ),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option(
            help="Log less on runtime.",
        ),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option(
            help="Log more on runtime.",
        ),
    ] = False,
) -> None:
    """Run the `mp build` command.

    Args:
        repository: the repository to build
        integration: the integrations to build
        group: the groups to build
        deconstruct: whether to deconstruct instead of build
        quiet: quiet log options
        verbose: Verbose log options

    """
    run_params: RuntimeParams = mp.core.config.RuntimeParams(quiet, verbose)
    run_params.set_in_config()

    params: BuildParams = BuildParams(repository, integration, group, deconstruct)
    params.validate()

    commercial_mp: Marketplace = Marketplace(mp.core.file_utils.get_commercial_path())
    community_mp: Marketplace = Marketplace(mp.core.file_utils.get_community_path())
    if integration:
        rich.print("Building integrations...")
        _build_integrations(set(integration), commercial_mp, deconstruct=deconstruct)
        _build_integrations(set(integration), community_mp, deconstruct=deconstruct)
        rich.print("Done building integrations.")

    elif group:
        rich.print("Building groups...")
        _build_groups(set(group), commercial_mp)
        _build_groups(set(group), community_mp)
        rich.print("Done building groups.")

    elif repository:
        repos: set[RepositoryType] = set(repository)
        if RepositoryType.COMMERCIAL in repos:
            rich.print("Building all integrations and groups in commercial repo...")
            commercial_mp.build()
            commercial_mp.write_marketplace_json()
            rich.print("Done Commercial integrations build.")

        if RepositoryType.COMMUNITY in repos:
            rich.print("Building all integrations and groups in third party repo...")
            community_mp.build()
            community_mp.write_marketplace_json()
            rich.print("Done third party integrations build.")

        if is_full_build(repository):
            rich.print("Checking for duplicate integrations...")
            raise_errors_for_duplicate_integrations(
                commercial_path=commercial_mp.out_path,
                community_path=commercial_mp.out_path,
            )
            rich.print("Done checking for duplicate integrations.")


def _build_integrations(
    integrations: Iterable[str],
    marketplace_: Marketplace,
    *,
    deconstruct: bool,
) -> None:
    valid_integrations_: set[pathlib.Path] = _get_marketplace_paths_from_names(
        integrations,
        marketplace_.path,
    )
    valid_integration_names: set[str] = {i.name for i in valid_integrations_}
    not_found: set[str] = set(integrations).difference(valid_integration_names)
    if not_found:
        rich.print(
            "The following integrations could not be found in"
            f" the {marketplace_.path.name} marketplace: {', '.join(not_found)}",
        )
    if valid_integrations_:
        rich.print(
            "Building the following integrations in the"
            f" the {marketplace_.path.name} marketplace:"
            f" {', '.join(valid_integration_names)}"
        )
        if deconstruct:
            marketplace_.deconstruct_integrations(valid_integrations_)

        else:
            marketplace_.build_integrations(valid_integrations_)

        marketplace_.validate_all_uv_lock_files(valid_integrations_)


def _build_groups(groups: Iterable[str], marketplace_: Marketplace) -> None:
    valid_groups: set[pathlib.Path] = _get_marketplace_paths_from_names(
        names=groups,
        marketplace_path=marketplace_.path,
    )
    valid_group_names: set[str] = {g.name for g in valid_groups}
    not_found: set[str] = set(groups).difference(valid_group_names)
    if not_found:
        rich.print(f"The following groups could not be found: {', '.join(not_found)}")

    if valid_groups:
        rich.print(f"Building the following groups: {', '.join(valid_group_names)}")
        marketplace_.build_groups(valid_groups)


def _get_marketplace_paths_from_names(
    names: Iterable[str],
    marketplace_path: pathlib.Path,
) -> set[pathlib.Path]:
    return {p for n in names if (p := marketplace_path / n).exists()}


def is_full_build(repositories: Sequence[RepositoryType]) -> bool:
    return len(repositories) == len(RepositoryType)
