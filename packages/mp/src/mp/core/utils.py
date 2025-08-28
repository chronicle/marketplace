"""Module containing general utility functions."""

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

import re
import sys
from typing import TypedDict

from mp.core.constants import WINDOWS_PLATFORM

SNAKE_PATTERN_1 = re.compile(r"(.)([A-Z][a-z]+)")
SNAKE_PATTERN_2 = re.compile(r"([a-z0-9])([A-Z])")
GIT_STATUS_REGEXP: re.Pattern[str] = re.compile(r"^[ A-Z?!]{2} ")
ERR_MSG_STRING_LIMIT: int = 256
TRIM_CHARS: str = " ... "


def get_python_version_from_version_string(version: str) -> str:
    """Get the smallest python version found in a version string.

    Examples:
        >>> v: str = ">=3.11,<3.13"
        >>> get_python_version_from_version_string(v)
        3.11


    Args:
        version: the version string containing versions

    Returns:
        The string of the version

    """
    versions: list[str] = re.findall(r"[<~>!=]={0,2}(\d+\.\d+)", version)
    version_tuples: list[tuple[int, int]] = []
    for v in versions:
        major, minor = v.split(".")
        version_tuples.append((int(major), int(minor)))

    version_tuples.sort()
    lowest_version: tuple[int, int] = version_tuples[0]
    return ".".join(map(str, lowest_version))


class _TypedDictType(TypedDict):
    """Wrapper for TypedDicts to allow for attribute access."""


def remove_none_entries_from_mapping(d: _TypedDictType, /) -> None:
    """Remove all the keys that have `None` value in place.

    Args:
        d: the mapping to remove keys that have `None` as the value

    """
    keys_to_remove: list[str] = [k for k, v in d.items() if v is None]
    for k in keys_to_remove:
        del d[k]  # type: ignore[misc]


def str_to_snake_case(s: str) -> str:
    """Change a string into snake_case.

    Args:
        s: the string to transform

    Returns:
        A new string with the value of the original string in snake_case

    """
    s = s.replace(" ", "").replace("-", "")
    s = re.sub(SNAKE_PATTERN_1, r"\1_\2", s)
    return re.sub(SNAKE_PATTERN_2, r"\1_\2", s).lower()


def trim_values(s: str, /) -> str:
    """Trims a given string if its length exceeds a defined limit and appends ellipses.

    The function is designed to enforce an upper length constraint for strings.

    Args:
        s: The input string to be trimmed if it exceeds the defined length limit.

    Returns:
        The trimmed string if the length of the input string exceeds the limit,
        otherwise the original string is returned.

    """
    padding: int = len(TRIM_CHARS)
    if len(s) > ERR_MSG_STRING_LIMIT:
        return f"{s[: ERR_MSG_STRING_LIMIT - padding * 2]}{TRIM_CHARS}{s[len(s) - padding :]}"

    return s


def is_windows() -> bool:
    """Determine if the current operating system is Windows.

    Returns:
        bool: True if the operating system is Windows, otherwise False.

    """
    return WINDOWS_PLATFORM in sys.platform
