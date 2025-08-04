from __future__ import annotations

import pytest
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from integrations.third_party.tools.actions.CheckListSubset import main as run_action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestCheckListSubset:

    @set_metadata(
        parameters={"Original": "1,2,3", "Subset": "2,3"},
        input_context={"case": {"id": "test_case_id"}, "source_identifier": "test_alert_id"},
    )
    def test_valid_subset(self, action_output: MockActionOutput) -> None:
        run_action()

        assert action_output.results.result_value is True
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "All items from the subset list are in the original list" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(
        parameters={"Original": "ка", "Subset": "мвпи"},
        input_context={"case": {"id": "test_case_id"}, "source_identifier": "test_alert_id"},
    )
    def test_invalid_subset_cyrillic(self, action_output: MockActionOutput) -> None:
        run_action()

        assert action_output.results.result_value is False
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "Found items which are not in the original list: мвпи" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(
        parameters={"Original": "1,2,3", "Subset": ""},
        input_context={"case": {"id": "test_case_id"}, "source_identifier": "test_alert_id"},
    )
    def test_empty_subset(self, action_output: MockActionOutput) -> None:
        run_action()

        assert action_output.results.result_value is True
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "All items from the subset list are in the original list" in action_output.results.output_message
        assert action_output.results.json_output is None

    @set_metadata(
        parameters={"Original": "", "Subset": "1"},
        input_context={"case": {"id": "test_case_id"}, "source_identifier": "test_alert_id"},
    )
    def test_empty_original_invalid_subset(self, action_output: MockActionOutput) -> None:
        run_action()

        assert action_output.results.result_value is False
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "Found items which are not in the original list: 1" in action_output.results.output_message
        assert action_output.results.json_output is None
