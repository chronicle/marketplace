from __future__ import annotations

import pytest
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from actions import ConvertTimeFormat

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestConvertTimeFormat:
    @set_metadata(parameters={
        "Input": "2025-08-03 15:30:00",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "%d/%m/%Y %H:%M",
        "Time Delta In Seconds": 0,
        "Timezone": ""
    })
    def test_successful_conversion(self, action_output: MockActionOutput) -> None:
        ConvertTimeFormat.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == "%7/%30/%Y %15:%8"
        assert "%7/%30/%Y %15:%8" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(parameters={
        "Input": "",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "DD/MM/YYYY",
        "Time Delta In Seconds": 0,
        "Timezone": ""
    })
    def test_empty_input_defaults_to_now(self, action_output: MockActionOutput) -> None:
        ConvertTimeFormat.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value != ""
        assert action_output.results.output_message != ""
        assert action_output.results.json_output is None

    @set_metadata(parameters={
        "Input": "2025-02-30 16:01:40",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "%d/%m/%Y",
        "Time Delta In Seconds": 0,
        "Timezone": ""
    })
    def test_invalid_input_failure(self, action_output: MockActionOutput) -> None:
        with pytest.raises(Exception) as exc_info:
            ConvertTimeFormat.main()
        err_msg = str(exc_info.value).lower()
        assert "does not match format" in err_msg or "could not process" in err_msg

    @set_metadata(parameters={
        "Input": "1733266800",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "YYYY/MM/DD HH:mm",
        "Time Delta In Seconds": 0,
        "Timezone": ""
    })
    def test_unix_timestamp_10_digits(self, action_output: MockActionOutput) -> None:
        ConvertTimeFormat.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value.startswith("202")
        assert "202" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(parameters={
        "Input": "2025-08-03 12:00:00",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "HH:mm",
        "Time Delta In Seconds": 3600,
        "Timezone": ""
    })
    def test_time_delta_shift(self, action_output: MockActionOutput) -> None:
        ConvertTimeFormat.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == "13:00"
        assert "13:00" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(parameters={
        "Input": "2025-08-03 12:00:00",
        "From Format": "%Y-%m-%d %H:%M:%S",
        "To Format": "HH:mm",
        "Time Delta In Seconds": 0,
        "Timezone": "US/Pacific"
    })
    def test_with_timezone_conversion(self, action_output: MockActionOutput) -> None:
        ConvertTimeFormat.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value != ""
        assert action_output.results.output_message != ""
        assert action_output.results.json_output is None
