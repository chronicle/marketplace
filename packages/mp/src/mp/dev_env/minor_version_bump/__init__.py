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

import math
import pathlib
from typing import Any

import rich
import toml
import typer

import mp.core.constants
import mp.core.file_utils
from mp.core.config import get_marketplace_path

from .utils import (
    VersionCache,
    calculate_dependencies_hash,
    load_and_validate_cache,
    update_built_def_file,
    update_cache_file,
    update_version_cache,
)

CONFIG_PATH = pathlib.Path.home() / ".mp_dev_env.json"
INTEGRATIONS_CACHE_DIR_NAME: str = ".integrations_cache"
VERSIONS_CACHE_FILE_NAME: str = "version_cache.yaml"


def minor_version_bump(
    integration_dir_built: pathlib.Path, integration_dir_non_built: pathlib.Path
) -> None:
    """Bump the minor version of an integration, to enable new venv creation.

    Args:
        integration_dir_built (pathlib.Path): The path to the built integration directory.
        integration_dir_non_built (pathlib.Path): The path to the non-built integration directory.

    Raises:
        typer.Exit: If the 'packages/mp' folder cannot be found in a parent directory.

    """
    try:
        integrations_cache_folder: pathlib.Path = (
            get_marketplace_path() / INTEGRATIONS_CACHE_DIR_NAME
        )
        integration_name = integration_dir_non_built.name

        pyproject_path: pathlib.Path = integration_dir_non_built / mp.core.constants.PROJECT_FILE
        pyproject_data: dict[str, Any] = toml.load(pyproject_path)
        current_major_version = math.floor(float(pyproject_data["project"]["version"]))

        previous_cache: VersionCache | None = load_and_validate_cache(
            integrations_cache_folder, integration_name, current_major_version
        )

        updated_hash: str = calculate_dependencies_hash(pyproject_data)

        updated_version_cache: VersionCache = update_version_cache(
            previous_cache, updated_hash, pyproject_data
        )

        update_cache_file(integrations_cache_folder, integration_dir_built, updated_version_cache)
        update_built_def_file(integration_dir_built, updated_version_cache)

    except FileNotFoundError as e:
        rich.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1) from e
