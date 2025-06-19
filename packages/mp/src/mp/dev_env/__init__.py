# Copyright (c) 2024, Your Company or Name
import json
from pathlib import Path

import typer

from .api import BackendAPI
from .utils import (
    CONFIG_PATH,
    build_integration,
    find_built_integration_dir,
    get_integration_identifier,
    load_dev_env_config,
    zip_integration_dir,
)

app = typer.Typer(
    help="Commands for interacting with the development environment (playground)"
)


@app.command()
def login(no_verify: bool = typer.Option(False, "--no-verify", help="Skip credential verification after saving.")) -> None:
    """Authenticate to the dev environment (playground)."""
    api_root = typer.prompt("API root (e.g. https://playground.example.com)")
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)
    config = {"api_root": api_root, "username": username, "password": password}
    with CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f)
    typer.echo(f"[dev-env] Credentials saved to {CONFIG_PATH}")

    if not no_verify:
        try:
            api = BackendAPI(api_root, username, password)
            api.login()
            typer.secho("[dev-env] ✅ Credentials verified successfully.", fg=typer.colors.GREEN)
        except Exception as e:
            CONFIG_PATH.unlink(missing_ok=True)
            typer.echo(f"[dev-env] Credential verification failed: {e}\nCredentials file removed.")
            raise typer.Exit(1)


@app.command()
def deploy(integration: str) -> None:
    """Build and deploy an integration to the dev environment (playground).

    Raises:
        typer.Exit: If the integration is not found or the build/upload fails.

    """
    config = load_dev_env_config()
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
        api = BackendAPI(config["api_root"], config["username"], config["password"])
        api.login()
        details = api.get_integration_details(zip_path)
        integration_id = details["identifier"]
        result = api.upload_integration(zip_path, integration_id)
        typer.echo(f"[dev-env] Upload result: {result}")
        typer.secho("[dev-env] ✅ Integration deployed successfully.", fg=typer.colors.GREEN)
    except Exception as e:
        typer.echo(f"[dev-env] Upload failed: {e}")
        raise typer.Exit(1) from e
