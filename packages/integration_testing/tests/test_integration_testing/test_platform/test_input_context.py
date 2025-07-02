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
from typing import TYPE_CHECKING

from TIPCommon.data_models import ScriptContext

from integration_testing.platform.input_context import get_mock_input_context

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson


def test_get_mock_input_context_from_none_context() -> None:
    expected_context: SingleJson = ScriptContext().to_json()

    str_context: str = get_mock_input_context(None).decode("utf-8-sig")
    context: SingleJson = json.loads(str_context)

    assert context == expected_context


def test_get_mock_input_context_from_json() -> None:
    context_json: SingleJson = {
        "parameters": {"name": "value"},
        "integration_identifier": "mock integration",
        "job_api_key": "api key",
    }

    str_context: str = get_mock_input_context(context_json).decode("utf-8-sig")
    context: SingleJson = json.loads(str_context)

    assert context["parameters"] == context_json["parameters"]
    assert context["integration_identifier"] == context_json["integration_identifier"]
    assert context["job_api_key"] == context_json["job_api_key"]


def test_parameters_and_params_provided_no_override_happens() -> None:
    context_json: SingleJson = {
        "parameters": {"name": "value"},
        "connector_info": {"params": [{"param_name": "name", "param_value": "value"}]},
    }

    str_context: str = get_mock_input_context(context_json).decode("utf-8-sig")
    context: SingleJson = json.loads(str_context)

    assert context["connector_info"]["params"] != context["parameters"]
    assert context["parameters"] == context_json["parameters"]
    assert context["connector_info"]["params"] == context_json["connector_info"]["params"]


def test_parameters_provided_without_params_so_values_are_copied() -> None:
    params: list[dict[str, str]] = [{"param_name": "name", "param_value": "value"}]
    context_json: SingleJson = {"parameters": {"name": "value"}}

    str_context: str = get_mock_input_context(context_json).decode("utf-8-sig")
    context: SingleJson = json.loads(str_context)

    assert context["connector_info"]["params"] == params
