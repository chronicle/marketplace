from __future__ import annotations

import pytest
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from integrations.third_party.tools.actions.SearchText import main as run_action

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestSearchText:

    @set_metadata(
        parameters={
            "Text": "write aii loop tit",
            "Search For": "",
            "Search For Regex": "",
            "Case Sensitive": "True",
        },
        input_context={"case": {"id": "test_case_id"}, "source_identifier": "test_alert_id"},
    )
    def test_missing_search_values(self, action_output: MockActionOutput) -> None:
        run_action()

        result = action_output.results.result_value
        state = action_output.results.execution_state
        json_output = action_output.results.json_output.json_result
        message = action_output.results.output_message

        assert result == "false"
        assert state == ExecutionState.FAILED
        assert json_output.get("matches") == []
        assert "Search For or Search For Regex must contain a value." in message
