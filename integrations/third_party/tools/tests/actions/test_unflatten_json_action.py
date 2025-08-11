from __future__ import annotations

import json
import pytest
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from ...actions import UnflattenJson

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestUnflattenJson:
    @set_metadata(
        parameters={
            "JSON Object": json.dumps({
                "user_name": "John",
                "user_age": 30,
                "address_city": "New York",
                "address_zip": "10001"
            }),
            "Delimiter": "_"
        }
    )
    def test_unflatten_json_success(self, action_output: MockActionOutput) -> None:
        UnflattenJson.main()

        result = action_output.results.result_value
        output_msg = action_output.results.output_message
        execution_state = action_output.results.execution_state
        json_output = action_output.results.json_output.json_result

        assert result is True
        assert execution_state.name == "COMPLETED"
        assert "finished successfully" in output_msg

        assert json_output["user"]["name"] == "John"
        assert json_output["user"]["age"] == 30
        assert json_output["address"]["city"] == "New York"
        assert json_output["address"]["zip"] == "10001"

    @set_metadata(
        parameters={
            "JSON Object": "lead_ore",
            "Delimiter": "_"
        }
    )
    def test_unflatten_json_invalid_json(self, action_output: MockActionOutput) -> None:
        UnflattenJson.main()

        result = action_output.results.result_value
        output_msg = action_output.results.output_message
        execution_state = action_output.results.execution_state

        assert result is False
        assert execution_state.name == "FAILED"
        assert "invalid JSON provided" in output_msg
