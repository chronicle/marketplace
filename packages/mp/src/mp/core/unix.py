"""Module for interacting with the operating system and executing shell commands."""

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

import subprocess as sp  # noqa: S404
import sys
from typing import IO, TYPE_CHECKING

from . import config, constants, file_utils

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterable, Iterator

COMMAND_ERR_MSG: str = "Error happened while executing a command: {0}"


class CommandError(Exception):
    """Error that happens during commands."""


def compile_core_integration_dependencies(
    project_path: pathlib.Path,
    requirements_path: pathlib.Path,
) -> None:
    """Compile/Export all project dependencies into a requirements' file.

    Args:
        project_path: the path to the project folder - one that contains a
            `pyproject.toml` file
        requirements_path: the path to the requirements' file to write the contents into

    Raises:
        CommandError: if a project is already initialized

    """
    python_version: str = (
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    )
    command: list[str] = [
        sys.executable,
        "-m",
        "uv",
        "export",
        "--project",
        str(project_path),
        "--output-file",
        str(requirements_path),
        "--no-hashes",
        "--no-dev",
        "--python",
        python_version,
    ]
    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        sp.run(command, cwd=project_path, check=True, text=True)  # noqa: S603
    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def download_wheels_from_requirements(
    requirements_path: pathlib.Path,
    dst_path: pathlib.Path,
) -> None:
    """Download `.whl` files from a requirements' file.

    Args:
        requirements_path: the path of the 'requirements.txt' file
        dst_path: the path to install the `.whl` files into

    Raises:
        CommandError: if a project is already initialized

    """
    python_version: str = _get_python_version()
    command: list[str] = [
        sys.executable,
        "-m",
        "pip",
        "download",
        "-r",
        str(requirements_path),
        "-d",
        str(dst_path),
        "--only-binary=:all:",
        "--python-version",
        python_version,
        "--implementation",
        "cp",
        "--platform",
        "none-any",
        "--platform",
        "manylinux_2_17_x86_64",
    ]
    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        sp.run(command, cwd=requirements_path.parent, check=True, text=True)  # noqa: S603
    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def add_dependencies_to_toml(
    project_path: pathlib.Path,
    requirements_path: pathlib.Path,
) -> None:
    """Add dependencies from requirements to a python project's TOML file.

    Args:
        project_path: the path to the project
        requirements_path: the path to the requirements to add

    Raises:
        CommandError: if a project is already initialized

    """
    python_version: str = _get_python_version()
    command: list[str] = [
        sys.executable,
        "-m",
        "uv",
        "add",
        "-r",
        str(requirements_path),
        "--python",
        python_version,
    ]
    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        sp.run(command, cwd=project_path, check=True, text=True)  # noqa: S603
    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def init_python_project_if_not_exists(project_path: pathlib.Path) -> None:
    """Initialize a python project in a folder.

    If a project is already initialized in there, nothing will happen.

    Args:
        project_path: the path to initialize the project

    """
    pyproject: pathlib.Path = project_path / constants.PROJECT_FILE
    if pyproject.exists():
        return

    initials: set[pathlib.Path] = set(project_path.iterdir())
    keep: set[pathlib.Path] = {
        project_path / constants.PROJECT_FILE,
        project_path / constants.LOCK_FILE,
    }

    init_python_project(project_path)

    paths: set[pathlib.Path] = set(project_path.iterdir())
    paths_to_remove: set[pathlib.Path] = paths.difference(initials).difference(keep)
    file_utils.remove_paths_if_exists(*paths_to_remove)


def init_python_project(project_path: pathlib.Path) -> None:
    """Initialize a python project in a folder.

    Args:
        project_path: the path to initialize the project

    Raises:
        CommandError: if a project is already initialized

    """
    python_version: str = _get_python_version()
    command: list[str] = [
        sys.executable,
        "-m",
        "uv",
        "init",
        "--no-readme",
        "--no-workspace",
        "--python",
        python_version,
    ]

    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        sp.run(command, cwd=project_path, check=True, text=True)  # noqa: S603
    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def ruff_check(paths: Iterable[pathlib.Path], /, **flags: bool | str) -> int:
    """Run `ruff check` on the provided paths.

    Returns:
        The status code

    """
    command: list[str] = [sys.executable, "-m", "ruff", "check"]
    return execute_command_and_get_output(command, paths, **flags)


def ruff_format(paths: Iterable[pathlib.Path], /, **flags: bool | str) -> int:
    """Run `ruff format` on the provided paths.

    Returns:
        The status code

    """
    command: list[str] = [sys.executable, "-m", "ruff", "format"]
    return execute_command_and_get_output(command, paths, **flags)


def mypy(paths: Iterable[pathlib.Path], /, **flags: bool | str) -> int:
    """Run `mypy` on the provided paths.

    Returns:
        The status code

    """
    command: list[str] = [sys.executable, "-m", "mypy"]
    return execute_command_and_get_output(command, paths, **flags)


def run_script_on_paths(
    script_path: pathlib.Path,
    test_paths: Iterable[pathlib.Path],
) -> int:
    """Run a custom script on the provided paths.

    Returns:
        A tuple of the status code and output

    """
    path: str = f"{script_path.resolve().absolute()}"
    chmod_command: list[str] = ["chmod", "+x", path]
    sp.run(chmod_command, check=True)  # noqa: S603
    command: list[str] = [f"{script_path.resolve().absolute()}"]
    return execute_command_and_get_output(command, test_paths)


def execute_command_and_get_output(
    command: list[str],
    paths: Iterable[pathlib.Path],
    **flags: bool | str,
) -> int:
    """Execute a command and capture its output and status code.

    Args:
        command: the command values to execute
        paths: path values for the command
        **flags: any command flags as keyword arguments

    Returns:
        The status code of the process

    Raises:
        CommandError: if a project is already initialized

    """
    command.extend(str(path) for path in paths)

    flags_: list[str] = get_flags_to_command(**flags)
    command.extend(flags_)

    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        process: sp.Popen[bytes] = sp.Popen(command)  # noqa: S603
        for line in _stream_process_output(process):
            sys.stdout.write(str(line))

        return process.wait()

    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def _stream_process_output(process: sp.Popen[bytes]) -> Iterator[bytes]:
    buffer: IO[bytes] | None = process.stdout
    if process.stdout is None:
        buffer = process.stderr

    if buffer is None:
        return

    line: bytes = buffer.readline()
    while line:
        yield line
        line = buffer.readline()


def get_changed_files() -> list[str]:
    """Get a list of file names that were changed since the last commit.

    Returns:
        A list of file names that were changed since the last commit.

    Raises:
        CommandError: The command failed to be executed

    """
    command: list[str] = [
        "/usr/bin/git",
        "diff",
        "HEAD^",
        "HEAD",
        "--name-only",
        "--diff-filter=ACMRTUXB",
    ]
    try:
        result: sp.CompletedProcess[str] = sp.run(  # noqa: S603
            command,
            check=True,
            text=True,
            capture_output=True,
        )
        return result.stdout.split()

    except sp.CalledProcessError as e:
        raise CommandError(COMMAND_ERR_MSG.format(e)) from e


def _get_runtime_config() -> list[str]:
    result: list[str] = []
    if config.is_quiet():
        result.append("--quiet")

    if config.is_verbose():
        result.append("--verbose")

    return result


def get_flags_to_command(**flags: bool | str | list[str]) -> list[str]:
    """Get all the kwarg flags as a string with the appropriate `-` or `--`.

    Examples:
        >>> get_flags_to_command(f=True, name="TIPCommon", files=["1", "2"])
        >>> "-f --name TIPCommon --files 1 2"

    Keyword Args:
        **flags: The flags to parse

    Returns:
        A string containing the flags for a command.

    """
    if not flags:
        return []

    all_flags: list[str] = []
    for flag, value in flags.items():
        f: str = flag.replace("_", "-")
        f = f"-{f}" if len(f) == 1 else f"--{f}"
        all_flags.append(f)
        if isinstance(value, bool):
            if value is False:
                all_flags.pop()

        elif isinstance(value, list):
            all_flags.extend(value)

        else:
            all_flags.append(value)

    return all_flags


def check_lock_file(project_path: pathlib.Path) -> None:
    """Check if the 'uv.lock' file is consistent with 'pyproject.toml' file.

    Args:
        project_path: The integration path to the project directory
                      that contains 'pyproject.toml' and 'uv.lock' files.

    Raises:
        CommandError: If the 'uv lock --check' command indicates that the
                      'uv.lock' file is out of sync or if another error
                      occurs during the check.

    """
    python_version: str = _get_python_version()

    command: list[str] = [
        sys.executable,
        "-m",
        "uv",
        "lock",
        "--check",
        "--project",
        str(project_path),
        "--python",
        python_version,
    ]

    runtime_config: list[str] = _get_runtime_config()
    command.extend(runtime_config)

    try:
        sp.run(  # noqa: S603
            command, cwd=project_path, check=True, text=True, capture_output=True
        )

    except sp.CalledProcessError as e:
        error_output = e.stderr.strip()
        error_output = (
            COMMAND_ERR_MSG.format("uv lock --check") + f" UV Lock Check Failed: {error_output}"
        )
        raise CommandError(error_output) from e


def _get_python_version() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
