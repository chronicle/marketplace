import json
import os
import subprocess
import zipfile
from pathlib import Path

import typer

from mp.core.data_models.integration import Integration

CONFIG_PATH = Path.home() / ".mp_dev_env.json"


def zip_integration_dir(integration_dir: Path) -> Path:
    zip_path = integration_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(integration_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(integration_dir)
                zipf.write(file_path, arcname)
    return zip_path


def load_dev_env_config():
    if not CONFIG_PATH.exists():
        typer.echo("[dev-env] Not logged in. Please run 'mp dev-env login' first.")
        raise typer.Exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def build_integration(integration: str):
    result = subprocess.run(
        ["mp", "build", "--integration", integration, "--quiet"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        typer.echo(f"[dev-env] Build failed:\n{result.stderr}")
        raise typer.Exit(result.returncode)
    typer.echo(f"[dev-env] Build output:\n{result.stdout}")


def get_integration_identifier(source_path: Path) -> str:
    try:
        integration_obj = Integration.from_non_built_path(source_path)
        return integration_obj.identifier
    except ValueError as e:
        typer.echo(f"[dev-env] Could not determine integration identifier: {e}")
        raise typer.Exit(1)


def find_built_integration_dir(source_path: Path, identifier: str) -> Path:
    root = Path.cwd() / "out" / "integrations"
    for repo in ["commercial", "third_party"]:
        candidate = root / repo / identifier
        if candidate.exists():
            return candidate
    typer.echo(
        f"[dev-env] Built integration not found for identifier '{identifier}' in out/integrations."
    )
    raise typer.Exit(1)
