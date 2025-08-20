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
from dataclasses import asdict, dataclass
from typing import Any

import rich
import yaml

import mp.core.constants
import mp.core.file_utils

CONFIG_PATH = pathlib.Path.home() / ".mp_dev_env.json"
INTEGRATIONS_CACHE_DIR_NAME: str = ".integrations_cache"
VERSIONS_CACHE_FILE_NAME: str = "version_cache.yaml"


@dataclass
class VersionCache:
    """A structured representation of the version cache data."""

    version: float
    hash: str
    next_version_change: float


def load_and_validate_cache(
    cache_folder: pathlib.Path, integration_name: str, current_major_version: int
) -> VersionCache | None:
    """Load and validates a cached version file.

    Args:
        cache_folder: The directory where the cache is stored.
        integration_name: The name of the integration, used to form the cache
            file path.
        current_major_version: The current major version number, used to validate
            the cache.

    Returns:
        A VersionCache object if a valid cache is found, otherwise None.

    """
    cache: VersionCache | None = _load_cached_version(cache_folder, integration_name)
    if not cache:
        return None
    if not _validate_cached_version(cache, current_major_version):
        (cache_folder / integration_name / VERSIONS_CACHE_FILE_NAME).unlink()
        return None
    return cache


def _load_cached_version(cache_folder: pathlib.Path, integration_name: str) -> VersionCache | None:
    integration_cache_dir = cache_folder / integration_name
    integration_cache_dir.mkdir(parents=True, exist_ok=True)
    version_file_path = integration_cache_dir / VERSIONS_CACHE_FILE_NAME
    if not version_file_path.exists():
        return None
    try:
        cached_data: dict[str, Any] = yaml.safe_load(version_file_path.read_text(encoding="utf-8"))
        return VersionCache(
            cached_data["version"], cached_data["hash"], cached_data["next_version_change"]
        )
    except (KeyError, TypeError):
        rich.print("[yellow]Cache file is invalid. Invalidating and removing old cache.[/yellow]")
        version_file_path.unlink(missing_ok=True)
        return None


def _validate_cached_version(cache: VersionCache, current_major_version: int) -> bool:
    cached_major_version = math.floor(cache.version)
    return current_major_version == cached_major_version


def calculate_dependencies_hash(pyproject_data: dict[str, Any]) -> str:
    """Calculate an MD5 hash of the project's dependencies.

    Args:
        pyproject_data: A dictionary representing the parsed content of a
            `pyproject.toml` file.

    Returns:
        A hexadecimal string representing the MD5 hash of the dependencies.

    """
    sections_to_hash: dict[str, Any] = {}
    if dependencies := pyproject_data.get("project", {}).get("dependencies"):
        sections_to_hash["dependencies"] = dependencies
    if dep_groups := pyproject_data.get("dependency-groups"):
        sections_to_hash["dependency-groups"] = dep_groups
    serialized_data: bytes = json.dumps(sections_to_hash, sort_keys=True, indent=None).encode(
        "utf-8"
    )
    return hashlib.md5(serialized_data).hexdigest()  # noqa: S324


def update_version_cache(
    previous_cache: VersionCache | None,
    updated_hash: str,
    pyproject_data: dict[str, Any],
) -> VersionCache:
    """Update the version cache based on a new hash and pyproject data.

    Args:
        previous_cache: The previous version cache, or None if it's the first
            cache being created.
        updated_hash: The new hash to be stored in the cache.
        pyproject_data: The data from the pyproject.toml file.

    Returns:
        A new `VersionCache` object with the updated version, hash, and next

    """
    plus_factor: float = 0.1
    minus_factor: float = -0.1
    updated_version: float
    next_change: float
    if previous_cache:
        updated_version, next_change = _update_existing_version_cache(previous_cache, updated_hash)
    else:
        base_version = float(pyproject_data["project"]["version"])
        updated_version = base_version + (plus_factor * 2)
        next_change = minus_factor

    return VersionCache(
        version=round(updated_version, 2),
        hash=updated_hash,
        next_version_change=next_change,
    )


def _update_existing_version_cache(
    previous_cache: VersionCache | None, updated_hash: str
) -> tuple[float, float]:
    plus_factor: float = 0.1
    minus_factor: float = -0.1
    if previous_cache.hash != updated_hash:
        updated_version = previous_cache.version + previous_cache.next_version_change
        next_change = (
            plus_factor if previous_cache.next_version_change == minus_factor else minus_factor
        )
    else:
        updated_version = previous_cache.version
        next_change = previous_cache.next_version_change

    return updated_version, next_change


def update_cache_file(
    cache_folder: pathlib.Path, integration_dir_built: pathlib.Path, updated_cache: VersionCache
) -> None:
    """Update the YAML cache file with the new version information.

    Args:
        cache_folder: The root directory for all cache files.
        integration_dir_built: The directory of the built integration.
        updated_cache: The VersionCache object containing the new version data.

    """
    integration_name = integration_dir_built.name
    version_file_path = cache_folder / integration_name / VERSIONS_CACHE_FILE_NAME
    with version_file_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(asdict(updated_cache), f)


def update_built_def_file(integration_dir_built: pathlib.Path, updated_cache: VersionCache) -> None:
    """Update the JSON definition file with the new version.

    Args:
        integration_dir_built: The directory of the built integration.
        updated_cache: The VersionCache object containing the new version data.

    """
    def_file_path = integration_dir_built / mp.core.constants.INTEGRATION_DEF_FILE.format(
        integration_dir_built.name
    )

    with def_file_path.open("r", encoding="utf-8") as f:
        def_data: dict[str, Any] = json.load(f)

    def_data["Version"] = updated_cache.version
    with def_file_path.open("w", encoding="utf-8") as f:
        json.dump(def_data, f, indent=4)
