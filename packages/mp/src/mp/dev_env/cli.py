from pathlib import Path

import typer

from .api import BackendAPI
from .utils import (
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
def login() -> None:
    api_root = typer.prompt("API root (e.g. https://playground.example.com)")
    username = typer.prompt("Username")
    password = typer.prompt("Password", hide_input=True)
    config = {"api_root": api_root, "username": username, "password": password}
    from .utils import CONFIG_PATH

    with CONFIG_PATH.open("w") as f:
        import json

        json.dump(config, f)
    typer.echo(f"[dev-env] Credentials saved to {CONFIG_PATH}")


@app.command()
def deploy(integration: str) -> None:
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
    except Exception as e:
        typer.echo(f"[dev-env] Upload failed: {e}")
        raise typer.Exit(1)
