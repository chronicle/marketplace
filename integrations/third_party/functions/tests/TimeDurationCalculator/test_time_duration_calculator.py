from __future__ import annotations
import json
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from integrations.third_party.functions.actions.TimeDurationCalculator import main as TimeDurationCalculator_main

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

class TestTimeDurationCalculator:

    @set_metadata(
        parameters={
            "Input DateTime 1": "2024-01-01T00:00:00+0000",
            "Input DateTime 1 Format": "%Y-%m-%dT%H:%M:%S%z",
            "Input DateTime 2": "2025-02-02T03:04:05+0000",
            "Input DateTime 2 Format": "%Y-%m-%dT%H:%M:%S%z",
        }
    )
    def test_time_duration_all_units(self, action_output: MockActionOutput) -> None:
        TimeDurationCalculator_main()
        results = action_output.results
        assert results.execution_state is ExecutionState.COMPLETED
        assert results.json_output is not None
        json_data = {}
        if hasattr(results.json_output, "json_result"):
            json_data = results.json_output.json_result
        elif hasattr(results.json_output, "to_dict"):
            json_data = results.json_output.to_dict()
        elif hasattr(results.json_output, "raw_json"):
            try:
                json_data = json.loads(results.json_output.raw_json)
            except Exception:
                json_data = {}
        elif isinstance(results.json_output, dict):
            json_data = results.json_output
        expected_keys = {"years", "days", "hours", "minutes", "seconds", "duration"}
        assert expected_keys <= json_data.keys()
        assert isinstance(results.result_value, int)
        assert "2024-01-01T00:00:00+0000" in results.output_message
        assert "2025-02-02T03:04:05+0000" in results.output_message
        assert "duration" in results.output_message.lower()
