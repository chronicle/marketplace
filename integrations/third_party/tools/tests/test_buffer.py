from __future__ import annotations
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from ..actions import Buffer

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

VALID_JSON_INPUT: str = '{"foo": "bar"}'
PARSED_JSON: dict = {"foo": "bar"}
INVALID_JSON_INPUT: str = '{"foo": "bar"'


class TestBuffer:

    @set_metadata(parameters={"JSON": VALID_JSON_INPUT, "ResultValue": "True"})
    def test_valid_json_success(self, action_output: MockActionOutput) -> None:
        Buffer.main()
        assert action_output.results.result_value == "True"
        assert action_output.results.output_message == "Input values 'transferred' to the output."
        assert action_output.results.json_output.json_result == PARSED_JSON
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"JSON": INVALID_JSON_INPUT, "ResultValue": "False"})
    def test_invalid_json_returns_error_message(self, action_output: MockActionOutput) -> None:
        Buffer.main()
        assert action_output.results.result_value == "False"
        assert "Input values 'transferred' to the output." in action_output.results.output_message
        assert "Failed to load JSON with error" in action_output.results.output_message
        assert action_output.results.json_output.json_result is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"JSON": "", "ResultValue": "Maybe"})
    def test_empty_json_parameter(self, action_output: MockActionOutput) -> None:
        Buffer.main()
        assert action_output.results.result_value == "Maybe"
        assert action_output.results.output_message == "Input values 'transferred' to the output."
        assert action_output.results.json_output.json_result is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"ResultValue": "42"})
    def test_missing_json_parameter(self, action_output: MockActionOutput) -> None:
        Buffer.main()
        assert action_output.results.result_value == "42"
        assert action_output.results.output_message == "Input values 'transferred' to the output."
        assert action_output.results.json_output.json_result is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED
