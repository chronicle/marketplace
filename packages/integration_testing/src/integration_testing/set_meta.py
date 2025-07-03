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

import functools
import inspect
import unittest.mock
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from TIPCommon.types import Entity, GeneralFunction, SingleJson, Supplier
from TIPCommon.utils import none_to_default_value

from .common import get_def_file_content, prepare_connector_params, prepare_job_params
from .platform.external_context import MockExternalContext
from .platform.input_context import get_mock_input_context

if TYPE_CHECKING:
    import pathlib

    from TIPCommon.base.job import JobParameter
    from TIPCommon.data_models import ConnectorParameter

TestFn = Callable[..., None]
PatchParams = tuple[str, GeneralFunction]


def set_metadata(  # noqa: PLR0913, PLR0917
    func: TestFn | None = None,
    parameters: SingleJson | None = None,
    entities: list[Entity] | None = None,
    input_context: SingleJson | None = None,
    external_context: MockExternalContext | None = None,
    integration_config_file_path: str | pathlib.Path | None = None,
    integration_config: SingleJson | None = None,
    job_def_file_path: str | pathlib.Path | None = None,
    connector_def_file_path: str | pathlib.Path | None = None,
) -> Callable[[TestFn], TestFn] | TestFn:
    """Set the metadata of a SecOps Marketplace script.

    Notes:
        - All parameters must be passed using keyword arguments, except func which
            should be passed implicitly as the decorator's argument
    Args:
        func: The wrapped function. Do not use this!
        parameters: The script's input parameters
        entities: A list of entities for actions to use
        input_context: The script's input context json
        external_context: External context for the script to use. Can be set with
            initial values, and is passed as an argument to the wrapped function so the
            results can be checked
        integration_config_file_path: The path to a donfig json file that contains the
            integration's configuration/authentication parameters
        integration_config: The integration's configuration
        job_def_file_path: The path to the job's ".jobdef" file. This must be used in
            jobs that use the Job base class
        connector_def_file_path: The path to the connector's ".connectordef" file.
            This must be used in connectors that use the Connector base class

    Returns:
        Runs the function it's decorating with all the mocks required to run
        a marketplace script.

    """
    input_context = none_to_default_value(input_context, {})
    integration_config = none_to_default_value(integration_config, {})
    parameters = none_to_default_value(parameters, {})
    entities = none_to_default_value(entities, [])
    ec = none_to_default_value(external_context, MockExternalContext())

    def decorator(fn: TestFn) -> TestFn:
        if "external_context" in inspect.signature(fn).parameters:
            fn = functools.partial(fn, external_context=ec)

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401
            json_context_path, mock_get_context = _get_json_context_patch_path_and_fn(
                parameters,
                input_context,
            )
            config_path, mock_get_config = _get_integration_config_path_and_fn(
                integration_config_file_path,
                integration_config,
            )
            job_params_path, mock_job_params = _get_job_parameters(
                job_def_file_path,
                parameters,
            )
            connector_params_path, mock_connector_params = _get_connector_parameters(
                connector_def_file_path,
                parameters,
            )
            set_db_context_path, mock_set_db_context = _get_set_context_path_and_fn(ec)
            get_db_context_path, mock_get_db_context = _get_get_context_path_and_fn(ec)
            entities_path, get_entities = _get_entities_path_and_fn(entities)

            with (
                unittest.mock.patch(json_context_path, mock_get_context),
                unittest.mock.patch(config_path, mock_get_config),
                unittest.mock.patch(set_db_context_path, mock_set_db_context),
                unittest.mock.patch(get_db_context_path, mock_get_db_context),
                unittest.mock.patch(job_params_path, mock_job_params),
                unittest.mock.patch(connector_params_path, mock_connector_params),
                unittest.mock.patch(entities_path, get_entities),
            ):
                fn(*args, **kwargs)

        return wrapper

    return decorator(func) if func is not None and callable(func) else decorator


def _get_json_context_patch_path_and_fn(
    parameters: SingleJson,
    json_context: SingleJson,
) -> PatchParams:
    if json_context.get("parameters") is None:
        json_context["parameters"] = parameters

    context_path: str = "SiemplifyBase.SiemplifyBase.get_script_context"
    mock_get_context: Supplier[SingleJson] = functools.partial(
        get_mock_input_context,
        context=json_context,
    )

    return context_path, mock_get_context


def _get_entities_path_and_fn(entities: list[Entity] | None) -> tuple[str, list[Entity] | None]:
    path: str = "SiemplifyAction.SiemplifyAction.target_entities"
    return path, entities


def _get_integration_config_path_and_fn(
    file_path: str | pathlib.Path | None,
    integration_config: SingleJson,
) -> PatchParams:
    path: str = "Siemplify.Siemplify.get_configuration_from_server"

    def mock_get_configuration() -> SingleJson:
        return integration_config

    if not integration_config:
        mock_get_configuration = functools.partial(get_def_file_content, def_file_path=file_path)

    return path, lambda *_: mock_get_configuration()


def _get_job_parameters(
    job_def_file: str | pathlib.Path | None,
    params: SingleJson,
) -> PatchParams:
    context_path: str = "TIPCommon.base.job.base_job.Job._Job__get_job_parameters"
    mock_get_job_params: Supplier[list[JobParameter]] = functools.partial(
        prepare_job_params,
        job_def_file=job_def_file,
        params=params,
    )
    return context_path, mock_get_job_params


def _get_connector_parameters(
    connector_def_file: str | pathlib.Path | None,
    params: SingleJson,
) -> PatchParams:
    context_path: str = "TIPCommon.extraction.get_connector_detailed_params"
    mock_get_connector_params: Supplier[list[ConnectorParameter]] = functools.partial(
        prepare_connector_params,
        connector_def_file=connector_def_file,
        params=params,
    )

    if "PythonProcessTimeout" not in params:
        params["PythonProcessTimeout"] = 180

    return context_path, lambda _: mock_get_connector_params()


def _get_set_context_path_and_fn(db: MockExternalContext) -> PatchParams:
    path: str = "SiemplifyBase.SiemplifyBase.set_context_property_in_server"
    return path, db.set_row_value


def _get_get_context_path_and_fn(db: MockExternalContext) -> PatchParams:
    path: str = "SiemplifyBase.SiemplifyBase.get_context_property_from_server"
    return path, db.get_row_value
