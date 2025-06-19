# Copyright (c) 2024, Your Company or Name
import json
import os
import subprocess  # noqa: S404
import zipfile
from pathlib import Path
from typing import Any

import typer

from mp.core.data_models.integration import Integration

CONFIG_PATH = Path.home() / ".mp_dev_env.json"


def zip_integration_dir(integration_dir: Path) -> Path:
    """Zip the contents of a built integration directory for upload.

    Args:
        integration_dir: Path to the built integration directory.

    Returns:
        Path: The path to the created zip file.

    """
    zip_path = integration_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(integration_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(integration_dir)
                zipf.write(file_path, arcname)
    return zip_path


def load_dev_env_config() -> dict[str, Any]:
    """Load the dev environment configuration from the config file.

    Returns:
        dict: The loaded configuration.

    Raises:
        typer.Exit: If the config file does not exist.

    """
    if not CONFIG_PATH.exists():
        typer.echo("[dev-env] Not logged in. Please run 'mp dev-env login' first.")
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
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.echo(f"[dev-env] Build failed:\n{result.stderr}")
        raise typer.Exit(result.returncode)
    typer.echo(f"[dev-env] Build output:\n{result.stdout}")


def get_integration_identifier(source_path: Path) -> str:
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
        typer.echo(f"[dev-env] Could not determine integration identifier: {e}")
        raise typer.Exit(1) from e
    else:
        return integration_obj.identifier


def find_built_integration_dir(_: Path, identifier: str) -> Path:
    """Find the built integration directory.

    Args:
        _: Unused source path argument.
        identifier: The integration identifier.

    Returns:
        Path: The path to the built integration directory.

    Raises:
        typer.Exit: If the built integration is not found.

    """
    root = Path.cwd() / "out" / "integrations"
    for repo in ["commercial", "third_party"]:
        candidate = root / repo / identifier
        if candidate.exists():
            return candidate
    typer.echo(
        f"[dev-env] Built integration not found for identifier '{identifier}' "
        "in out/integrations."
    )
    raise typer.Exit(1)
