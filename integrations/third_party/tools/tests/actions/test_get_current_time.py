from __future__ import annotations

import re

import pytest
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import GetCurrentTime

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestGetCurrentTime:
    @set_metadata(
        parameters={
            "Datetime Format": "%d/%m/%Y %H:%M"
        }
    )
    def test_get_current_time_success(self, action_output: MockActionOutput) -> None:
        # Act
        GetCurrentTime.main()

        # Assert
        result = action_output.results.result_value
        output_message = action_output.results.output_message
        execution_state = action_output.results.execution_state
        json_output = action_output.results.json_output

        # Проверки
        assert result is not None
        assert execution_state.name == "COMPLETED"
        assert "output message" in output_message

        # Проверка соответствия формату "%d/%m/%Y %H:%M"
        pattern = r"\d{2}/\d{2}/\d{4} \d{2}:\d{2}"
        assert re.fullmatch(pattern, result)

        # JSON Output должен быть пустым
        assert json_output is None or json_output == {}
