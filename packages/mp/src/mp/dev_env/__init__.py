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

import json
import pathlib
from typing import Annotated, NamedTuple

import rich
import typer

from . import api, utils

app = typer.Typer(help="Commands for interacting with the development environment (playground)")


class DevEnvParams(NamedTuple):
    username: str
    password: str
    api_root: str


@app.command(
    help=(
        "Set the login parameters for the SOAR environment you want to push response integrations"
        " to"
    )
)
def login(
    api_root: Annotated[
        str | None,
        typer.Option(
            "--api-root",
            help="API root (e.g. https://playground.example.com). If not provided, will prompt.",
        ),
    ] = None,
    username: Annotated[
        str | None,
        typer.Option(
            "--username",
            help="Username for authentication. If not provided, will prompt.",
        ),
    ] = None,
    password: Annotated[
        str | None,
        typer.Option(
            "--password",
            help="Password for authentication. If not provided, will prompt.",
            hide_input=True,
        ),
    ] = None,
    *,
    no_verify: Annotated[
        bool,
        typer.Option(
            "--no-verify",
            help="Skip credential verification after saving.",
        ),
    ] = False,
) -> None:
    """Authenticate to the dev environment (playground).

    Args:
        api_root: The API root of the dev environment.
        username: The username to authenticate with.
        password: The password to authenticate with.
        no_verify: Skip credential verification after saving.

    Raises:
        typer.Exit: If the API root, username, or password is not provided.

    """
    if api_root is None:
        api_root = typer.prompt("API root (e.g. https://playground.example.com)")
    if username is None:
        username = typer.prompt("Username")
    if password is None:
        password = typer.prompt("Password", hide_input=True)

    if api_root is None or username is None or password is None:
        rich.print(
            "API root, username, and password are required. "
            "Please provide them using the"
            "--api-root, --username, and --password options."
            "Or run 'mp dev-env login' to be prompted for them."
        )
        raise typer.Exit(1)

    params = DevEnvParams(username=username, password=password, api_root=api_root)
    config = {
        "api_root": params.api_root,
        "username": params.username,
        "password": params.password,
    }
    with utils.CONFIG_PATH.open("w", encoding="utf-8") as f:
        json.dump(config, f)
    rich.print(f"Credentials saved to {utils.CONFIG_PATH}")

    if not no_verify:
        try:
            backend_api = api.BackendAPI(params.api_root, params.username, params.password)
            backend_api.login()
            rich.print("[green]✅ Credentials verified successfully.[/green]")
        except Exception as e:
            utils.CONFIG_PATH.unlink(missing_ok=True)
            rich.print(f"[red]Credential verification failed: {e}\nCredentials file removed.[/red]")
            raise typer.Exit(1) from e


@app.command(help="Deploy an integration to the SOAR environment configured by the login command.")
def deploy(integration: str = typer.Argument(..., help="Integration to build and deploy.")) -> None:
    """Build and deploy an integration to the dev environment (playground).

    Args:
        integration: The integration to build and deploy.

    Raises:
        typer.Exit: If the integration is not found.

    """
    config = utils.load_dev_env_config()
    integrations_root = pathlib.Path.cwd() / "integrations"
    source_path = None

    for repo in ["commercial", "third_party"]:
        candidate = integrations_root / repo / integration
        if candidate.exists():
            source_path = candidate
            break

    if not source_path:
        rich.print(
            f"[red]Could not find source integration "
            f"at integrations/commercial|third_party/{integration}[/red]"
        )
        raise typer.Exit(1)

    identifier = utils.get_integration_identifier(source_path)
    utils.build_integration(integration)
    built_dir = utils.find_built_integration_dir(source_path, identifier)
    zip_path = utils.zip_integration_dir(built_dir)
    rich.print(f"Zipped built integration at {zip_path}")

    try:
        backend_api = api.BackendAPI(config["api_root"], config["username"], config["password"])
        backend_api.login()
        details = backend_api.get_integration_details(zip_path)
        integration_id = details["identifier"]
        result = backend_api.upload_integration(zip_path, integration_id)
        rich.print(f"Upload result: {result}")
        rich.print("[green]✅ Integration deployed successfully.[/green]")
    except Exception as e:
        rich.print(f"[red]Upload failed: {e}[/red]")
        raise typer.Exit(1) from e
