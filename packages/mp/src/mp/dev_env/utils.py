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

import rich
import toml
import typer
import yaml

import mp.core.constants
import mp.core.file_utils
from mp.core.data_models.integration import Integration

CONFIG_PATH = pathlib.Path.home() / ".mp_dev_env.json"


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

    """
    plus_factor = 0.1
    minus_factor = -0.1

    pyproject_path = integration_dir_non_built / "pyproject.toml"
    pyproject_data = toml.load(pyproject_path)
    version_file_path = integration_dir_non_built / ".integration_cache" / "version_cache.yml"

    versions_cache: dict = _create_files(pyproject_data, integration_dir_non_built)

    updated_hash: str = _calculate_hash(pyproject_data)
    updated_version: float
    next_version_change: float

    if versions_cache:
        previous_version: float = float(versions_cache["version"])
        previous_hash: str = versions_cache["hash"]
        previous_next_version_change = versions_cache["next_version_change"]

        if previous_hash != updated_hash:
            updated_version = previous_version + previous_next_version_change
            next_version_change = (
                plus_factor if previous_next_version_change == minus_factor else minus_factor
            )
        else:
            updated_version = previous_version
            next_version_change = previous_next_version_change
    else:
        updated_version = float(pyproject_data["project"]["version"]) + 0.2
        next_version_change = minus_factor

    versions_cache = {
        "version": updated_version,
        "hash": updated_hash,
        "next_version_change": next_version_change,
    }

    with version_file_path.open("w") as version_file:
        yaml.safe_dump(versions_cache, version_file)

    def_file_path = integration_dir_built / f"Integration-{integration_dir_built.name}.def"
    with def_file_path.open("r") as def_file:
        def_data = json.load(def_file)

    def_data["Version"] = updated_version
    with def_file_path.open("w") as def_file:
        json.dump(def_data, def_file, indent=4)


def _create_files(pyproject_data: dict, integration_dir_non_built: pathlib.Path) -> dict:
    resources_path = integration_dir_non_built / ".integration_cache"
    resources_path.mkdir(exist_ok=True)
    version_file_path = resources_path / "version_cache.yml"

    new_major_version = math.floor(float(pyproject_data["project"]["version"]))
    versions_cache: dict = {}

    if version_file_path.exists():
        with version_file_path.open("r") as f:
            versions_cache = yaml.safe_load(f) or {}
            if versions_cache and "version" in versions_cache:
                cached_major_version = int(float(versions_cache["version"]))
                if new_major_version != cached_major_version:
                    version_file_path.unlink(missing_ok=True)
                    return {}
    return versions_cache


def _calculate_hash(pyproject_data: dict) -> str:
    sections_to_hash = {}
    if "project" in pyproject_data and "dependencies" in pyproject_data["project"]:
        sections_to_hash["dependencies"] = pyproject_data["project"]["dependencies"]

    if "dependency-groups" in pyproject_data:
        sections_to_hash["dependency-groups"] = pyproject_data["dependency-groups"]
    serialized_data = json.dumps(sections_to_hash, sort_keys=True, indent=None).encode("utf-8")
    return hashlib.md5(serialized_data).hexdigest()  # noqa: S324
