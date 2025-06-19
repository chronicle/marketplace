import base64
import json
import os
import subprocess
import zipfile
from pathlib import Path

import requests
import typer

from mp.core.data_models.integration import Integration

app = typer.Typer(help="Commands for interacting with the development environment (playground)")

CONFIG_PATH = Path.home() / ".mp_dev_env.json"


def zip_integration_dir(integration_dir: Path) -> Path:
    """Zip the contents of a built integration directory for upload."""
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
    """Invoke the build command for a single integration."""
    result = subprocess.run([
        "mp", "build", "--integration", integration, "--quiet"
    ], check=False, capture_output=True, text=True)
    if result.returncode != 0:
        typer.echo(f"[dev-env] Build failed:\n{result.stderr}")
        raise typer.Exit(result.returncode)
    typer.echo(f"[dev-env] Build output:\n{result.stdout}")


def get_integration_identifier(source_path: Path) -> str:
    """Get the integration identifier from the non-built integration path."""
    try:
        integration_obj = Integration.from_non_built_path(source_path)
        return integration_obj.identifier
    except ValueError as e:
        typer.echo(f"[dev-env] Could not determine integration identifier: {e}")
        raise typer.Exit(1)


def find_built_integration_dir(source_path: Path, identifier: str) -> Path:
    """Find the built integration directory in out/integrations/COMMERCIAL|third_party/<Identifier>"""
    root = Path.cwd() / "out" / "integrations"
    for repo in ["commercial", "third_party"]:
        candidate = root / repo / identifier
        if candidate.exists():
            return candidate
    typer.echo(f"[dev-env] Built integration not found for identifier '{identifier}' in out/integrations.")
    raise typer.Exit(1)


def upload_integration(zip_path: Path, integration: str, config: dict) -> dict:
    # Login to get token
    login_url = f"{config['api_root'].rstrip('/')}/api/external/v1/accounts/Login?format=camel"
    login_payload = {"userName": config["username"], "password": config["password"]}
    resp = requests.post(login_url, json=login_payload, verify=False)
    resp.raise_for_status()
    token = resp.json()["token"]

    # Get integration details (identifier)
    details_url = f"{config['api_root'].rstrip('/')}/api/external/v1/ide/GetPackageDetails?format=camel"
    with open(zip_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    details_payload = {"data": data}
    resp = requests.post(details_url, json=details_payload, headers={"Authorization": f"Bearer {token}"}, verify=False)
    resp.raise_for_status()
    integration_id = resp.json()["identifier"]

    # Upload integration
    upload_url = f"{config['api_root'].rstrip('/')}/api/external/v1/ide/ImportPackage?format=camel"
    upload_payload = {
        "data": data,
        "integrationIdentifier": integration_id,
        "isCustom": False
    }
    resp = requests.post(upload_url, json=upload_payload, headers={"Authorization": f"Bearer {token}"}, verify=False)
    resp.raise_for_status()
    return resp.json()


@app.command()
def login() -> None:
    """Authenticate to the dev environment (playground)."""
    api_root = typer.prompt("API root (e.g. https://playground.example.com)")
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)
    config = {
        "api_root": api_root,
        "username": username,
        "password": password
    }
    with CONFIG_PATH.open("w") as f:
        json.dump(config, f)
    typer.echo(f"[dev-env] Credentials saved to {CONFIG_PATH}")


@app.command()
def deploy(integration: str) -> None:
    """Build and deploy an integration to the dev environment (playground).

    Args:
        integration: The name of the integration to deploy.

    Raises:
        typer.Exit: If the integration is not found or the build fails.

    """
    config = load_dev_env_config()
    # Find the source path for the integration
    integrations_root = Path.cwd() / "integrations"
    source_path = None
    for repo in ["commercial", "third_party"]:
        candidate = integrations_root / repo / integration
        if candidate.exists():
            source_path = candidate
            break
    if not source_path:
        typer.echo(
            "[dev-env] Could not find source integration "
            f"at integrations/commercial|third_party/{integration}"
        )
        raise typer.Exit(1)
    identifier = get_integration_identifier(source_path)
    build_integration(integration)
    built_dir = find_built_integration_dir(source_path, identifier)
    zip_path = zip_integration_dir(built_dir)
    typer.echo(f"[dev-env] Zipped built integration at {zip_path}")
    try:
        result = upload_integration(zip_path, integration, config)
        typer.echo(f"[dev-env] Upload result: {result}")
    except Exception as e:  # noqa: BLE001
        typer.echo(f"[dev-env] Upload failed: {e}")
        raise typer.Exit(1)  # noqa: B904
