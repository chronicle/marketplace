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

import hashlib
import json
import math
import pathlib
import shutil
import subprocess  # noqa: S404
from dataclasses import asdict, dataclass
from typing import Any

import rich
import toml
import typer
import yaml

import mp.core.constants
import mp.core.file_utils
from mp.core.data_models.integration import Integration

CONFIG_PATH = pathlib.Path.home() / ".mp_dev_env.json"
INTEGRATIONS_CACHE_DIR_NAME: str = ".integrations_cache"


@dataclass
class VersionCache:
    """A structured representation of the version cache data."""

    version: float
    hash: str
    next_version_change: float


def zip_integration_dir(integration_dir: pathlib.Path) -> pathlib.Path:
    """Zip the contents of a built integration directory for upload.

    Args:
        integration_dir: Path to the built integration directory.

    Returns:
        Path: The path to the created zip file.

    """
    return pathlib.Path(shutil.make_archive(str(integration_dir), "zip", integration_dir))


def load_dev_env_config() -> dict[str, str]:
    """Load the dev environment configuration from the config file.

    Returns:
        dict: The loaded configuration.

    Raises:
        typer.Exit: If the config file does not exist.

    """
    if not CONFIG_PATH.exists():
        rich.print("[red] Not logged in. Please run 'mp dev-env login' first. [/red]")
        raise typer.Exit(1)
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def build_integration(integration: str) -> None:
    """Invoke the build command for a single integration.

    Args:
        integration: The name of the integration to build.

    Raises:
        typer.Exit: If the build fails.

    """
    result = subprocess.run(  # noqa: S603
        ["mp", "build", "--integration", integration, "--quiet"],  # noqa: S607
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        rich.print(f"[red]Build failed:\n{result.stderr}[/red]")
        raise typer.Exit(result.returncode)

    rich.print(f"Build output:\n{result.stdout}")


def get_integration_identifier(source_path: pathlib.Path) -> str:
    """Get the integration identifier from the non-built integration path.

    Args:
        source_path: Path to the integration source directory.

    Returns:
        str: The integration identifier.

    Raises:
        typer.Exit: If the identifier cannot be determined.

    """
    try:
        integration_obj = Integration.from_non_built_path(source_path)
    except ValueError as e:
        rich.print(f"[red]Could not determine integration identifier: {e}[/red]")
        raise typer.Exit(1) from e
    else:
        return integration_obj.identifier


def find_built_integration_dir(_: pathlib.Path, identifier: str) -> pathlib.Path:
    """Find the built integration directory.

    Args:
        _: Unused source path argument.
        identifier: The integration identifier.

    Returns:
        Path: The path to the built integration directory.

    Raises:
        typer.Exit: If the built integration is not found.

    """
    root = mp.core.file_utils.get_out_integrations_path()
    for repo in mp.core.constants.INTEGRATIONS_TYPES:
        candidate = root / repo / identifier
        if candidate.exists():
            return candidate
    rich.print(
        f"[red]Built integration not found for identifier '{identifier}' in out/integrations.[/red]"
    )
    raise typer.Exit(1)


def minor_version_bump(
    integration_dir_built: pathlib.Path, integration_dir_non_built: pathlib.Path
) -> None:
    """Bump the minor version of an integration, to enable new venv creation.

    Args:
        integration_dir_built (pathlib.Path): The path to the built integration directory.
        integration_dir_non_built (pathlib.Path): The path to the non-built integration directory.

    Raises:
        FileNotFoundError: If the 'packages/mp' folder cannot be found in a parent directory.

    """
    try:
        integrations_cache_folder: pathlib.Path = find_project_root() / INTEGRATIONS_CACHE_DIR_NAME
        integration_name = integration_dir_non_built.name

        pyproject_path: pathlib.Path = integration_dir_non_built / "pyproject.toml"
        pyproject_data: dict[str, Any] = toml.load(pyproject_path)
        current_major_version = math.floor(float(pyproject_data["project"]["version"]))

        previous_cache: VersionCache = _load_and_validate_cache(
            integrations_cache_folder, integration_name, current_major_version
        )

        updated_hash: str = _calculate_dependencies_hash(pyproject_data)

        updated_version_cache: VersionCache = _update_version_cache(
            previous_cache, updated_hash, pyproject_data
        )

        _update_files(integrations_cache_folder, integration_dir_built, updated_version_cache)

    except FileNotFoundError as e:
        rich.print(f"[red]Error: {e}[/red]")
        raise


def find_project_root() -> pathlib.Path:
    """Search for the 'packages/mp' folder from the current directory.

    Returns:
        pathlib.Path: The absolute path to the 'packages/mp' folder if found.

    Raises:
        FileNotFoundError: If the project root could not be located.

    """
    current_dir: pathlib.Path = pathlib.Path(__file__)
    for parent in current_dir.parents:
        if parent.name == "packages":
            return parent / "mp"

    error_msg: str = "Could not find project root 'packages/mp' folder."
    raise FileNotFoundError(error_msg)


def _load_and_validate_cache(
    cache_folder: pathlib.Path, integration_name: str, current_major_version: int
) -> VersionCache | None:
    integration_cache_dir = cache_folder / integration_name
    integration_cache_dir.mkdir(parents=True, exist_ok=True)
    version_file_path = integration_cache_dir / "version_cache.yaml"

    if not version_file_path.exists():
        return None

    try:
        cached_data = yaml.safe_load(version_file_path.read_text(encoding="utf-8"))
        cached_major_version = math.floor(cached_data["version"])

        if current_major_version != cached_major_version:
            version_file_path.unlink()
            return None

        return VersionCache(**cached_data)

    except (KeyError, TypeError):
        rich.print("[yellow]Cache file is invalid. Invalidating and removing old cache.[/yellow]")
        version_file_path.unlink(missing_ok=True)
        return None


def _calculate_dependencies_hash(pyproject_data: dict[str, Any]) -> str:
    sections_to_hash: dict[str, Any] = {}
    if "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
        sections_to_hash["dependencies"] = pyproject_data["project"]["dependencies"]

    if "dependency-groups" in pyproject_data:
        sections_to_hash["dependency-groups"] = pyproject_data["dependency-groups"]
    serialized_data: bytes = json.dumps(sections_to_hash, sort_keys=True, indent=None).encode(
        "utf-8"
    )
    return hashlib.md5(serialized_data).hexdigest()  # noqa: S324


def _update_version_cache(
    previous_cache: VersionCache | None,
    updated_hash: str,
    pyproject_data: dict[str, Any],
) -> VersionCache:
    plus_factor: float = 0.1
    minus_factor: float = -0.1

    if previous_cache:
        if previous_cache.hash != updated_hash:
            updated_version = previous_cache.version + previous_cache.next_version_change
            next_change = (
                plus_factor if previous_cache.next_version_change == minus_factor else minus_factor
            )
        else:
            updated_version = previous_cache.version
            next_change = previous_cache.next_version_change
    else:
        base_version = float(pyproject_data["project"]["version"])
        updated_version = base_version + (plus_factor * 2)
        next_change = minus_factor

    return VersionCache(
        version=round(updated_version, 2),
        hash=updated_hash,
        next_version_change=next_change,
    )


def _update_files(
    cache_folder: pathlib.Path,
    integration_dir_built: pathlib.Path,
    updated_cache: VersionCache,
) -> None:
    integration_name = integration_dir_built.name
    version_file_path = cache_folder / integration_name / "version_cache.yaml"
    with version_file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(asdict(updated_cache), f)

    def_file_path = integration_dir_built / f"Integration-{integration_name}.def"

    with def_file_path.open("r", encoding="utf-8") as f:
        def_data: dict[str, Any] = json.load(f)

    def_data["Version"] = updated_cache.version
    with def_file_path.open("w", encoding="utf-8") as f:
        json.dump(def_data, f, indent=4)
