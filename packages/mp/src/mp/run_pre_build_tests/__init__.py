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
import pathlib
import warnings
from typing import TYPE_CHECKING, Annotated

import rich
import typer

import mp.build_project.marketplace
import mp.core.code_manipulation
import mp.core.config
import mp.core.file_utils
import mp.core.unix
from mp.core.custom_types import Products, RepositoryType

if TYPE_CHECKING:
    from collections.abc import Iterable

    from mp.core.config import RuntimeParams

RUN_PRE_BUILD_TESTS_PATH: pathlib.Path = (
    pathlib.Path(__file__).parent / "run_pre_build_tests.sh"
)

__all__: list[str] = ["app"]
app: typer.Typer = typer.Typer()


@dataclasses.dataclass(slots=True, frozen=True)
class TestParams:
    repository: Iterable[RepositoryType]
    integrations: Iterable[str]
    groups: Iterable[str]

    def validate(self) -> None:
        """Validate the parameters.

        Validates input parameters to ensure that only one parameter among
        `--repository`, `--groups`,
         or `--integration` is used during execution.

        Raises appropriate error messages if none or more than one of these
        parameters is specified.

        Raises:
            typer.BadParameter: If none of `--repository`, `--groups`, or
                `--integration` is provided or more than one of them is used.

        """
        params: list[Iterable[str] | Iterable[RepositoryType]] = self._as_list()
        msg: str
        if not any(params):
            msg = (
                "At least one of --repository, --groups, or --integration must be used."
            )
            raise typer.BadParameter(msg)

        if sum(map(bool, params)) != 1:
            msg = "Only one of --repository, --groups, or --integration shall be used."
            raise typer.BadParameter(msg)

    def _as_list(self) -> list[Iterable[RepositoryType] | Iterable[str]]:
        return [self.repository, self.integrations, self.groups]


@app.command(name="test", help="Run integration pre_build tests")
def run_pre_build_tests(  # noqa: PLR0913
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
    raise_error_on_violations: Annotated[
        bool,
        typer.Option(
            help="Whether to raise error on lint and type check violations",
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
    """Run the `mp test` command.

    Args:
        repository: the repository to build
        integration: the integrations to build
        group: the groups to build
        raise_error_on_violations: whether to raise error if any violations are found
        quiet: quiet log options
        verbose: Verbose log options

    """
    if raise_error_on_violations:
        warnings.filterwarnings("error")

    run_params: RuntimeParams = mp.core.config.RuntimeParams(quiet, verbose)
    run_params.set_in_config()

    params: TestParams = TestParams(repository, integration, group)
    params.validate()

    commercial_path: pathlib.Path = mp.core.file_utils.get_commercial_path()
    community_path: pathlib.Path = mp.core.file_utils.get_community_path()
    if integration:
        rich.print("Testing integrations...")
        _test_integrations(set(integration), commercial_path)
        _test_integrations(set(integration), community_path)
        rich.print("Done testing integrations.")

    elif group:
        rich.print("Testing groups...")
        _test_groups(set(group), commercial_path)
        _test_groups(set(group), community_path)
        rich.print("Done testing groups.")

    elif repository:
        repos: set[RepositoryType] = set(repository)
        if RepositoryType.COMMERCIAL in repos:
            rich.print("Testing all integrations and groups in commercial repo...")
            _test_repository(commercial_path)
            rich.print("Done testing commercial integrations.")

        if RepositoryType.COMMUNITY in repos:
            rich.print("Testing all integrations and groups in third party repo...")
            _test_repository(community_path)
            rich.print("Done testing third party integrations.")


def _test_repository(repo: pathlib.Path) -> None:
    products: Products[set[pathlib.Path]] = (
        mp.core.file_utils.get_integrations_and_groups_from_paths(repo)
    )
    if products.integrations:
        _test_integrations(products.integrations, repo)

    if products.groups:
        _test_groups(products.groups, repo)


def _test_groups(
    groups: Iterable[str | pathlib.Path],
    marketplace_path: pathlib.Path,
) -> None:
    valid_groups: set[pathlib.Path] = _get_marketplace_paths_from_names(
        names=groups,
        marketplace_path=marketplace_path,
    )
    valid_group_names: set[str] = {g.name for g in valid_groups}
    not_found: set[str] = set(map(str, groups)).difference(valid_group_names)
    if not_found:
        rich.print(f"The following groups could not be found: {', '.join(not_found)}")

    if valid_groups:
        rich.print(f"Testing the following groups: {', '.join(valid_group_names)}")
        for group in valid_groups:
            _test_integrations(group.iterdir(), marketplace_path)


def _test_integrations(
    integrations: Iterable[str | pathlib.Path],
    marketplace_path: pathlib.Path,
) -> None:
    valid_integrations_: set[pathlib.Path] = _get_marketplace_paths_from_names(
        names=integrations,
        marketplace_path=marketplace_path,
    )
    valid_integration_names: set[str] = {i.name for i in valid_integrations_}
    not_found: set[str] = set(map(str, integrations)).difference(
        valid_integration_names
    )
    if not_found:
        rich.print(
            "The following integrations could not be found in"
            f" the {marketplace_path.name} marketplace: {', '.join(not_found)}",
        )
    if valid_integrations_:
        rich.print(
            "Testing the following integrations in the"
            f" the {marketplace_path.name} marketplace:"
            f" {', '.join(valid_integration_names)}"
        )
        mp.core.code_manipulation.run_script_on_paths(
            script_path=RUN_PRE_BUILD_TESTS_PATH,
            paths=valid_integrations_,
        )


def _get_marketplace_paths_from_names(
    names: Iterable[str | pathlib.Path],
    marketplace_path: pathlib.Path,
) -> set[pathlib.Path]:
    results: set[pathlib.Path] = set()
    for name in names:
        if isinstance(name, str) and (p := marketplace_path / name).exists():
            results.add(p)

        elif isinstance(name, pathlib.Path) and name.exists():
            results.add(name)

    return results
