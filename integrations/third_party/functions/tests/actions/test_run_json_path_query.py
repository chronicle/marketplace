from __future__ import annotations
import pytest
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from actions import RunJsonpathQuery

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestRunJsonPathQuery:
    @set_metadata(parameters={
        "Json": '{"users": [{"name": "Alice"}, {"name": "Bob"}]}',
        "JSONPath Expression": "$.users[*].name"
    })
    def test_successful_query(self, action_output: MockActionOutput) -> None:
        RunJsonpathQuery.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        result = action_output.results.json_output.json_result
        assert "Alice" in result["matches"]
        assert "Bob" in result["matches"]
        assert action_output.results.json_output is not None

    @set_metadata(parameters={
        "Json": '{"users": [}',  # Невалидный JSON
        "JSONPath Expression": "$.users[*].name"
    })
    def test_invalid_json_exception(self) -> None:
        with pytest.raises(Exception):
            RunJsonpathQuery.main()

    @set_metadata(parameters={
        "Json": '{"users": [{"name": "Alice"}]}',
        "JSONPath Expression": "$.nonexistent[*]"
    })
    def test_no_matches_returns_empty(self, action_output: MockActionOutput) -> None:
        RunJsonpathQuery.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        result = action_output.results.json_output.json_result
        assert result == {"matches": []}

    @set_metadata(parameters={
        "Json": '{}',  # Пустой JSON
        "JSONPath Expression": "$.users[*].name"
    })
    def test_empty_json_returns_empty_matches(self, action_output: MockActionOutput) -> None:
        RunJsonpathQuery.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        result = action_output.results.json_output.json_result
        assert result == {"matches": []}

    @set_metadata(parameters={
        "Json": '',  # Полностью пустая строка
        "JSONPath Expression": "$.users[*].name"
    })
    def test_empty_input_exception(self) -> None:
        with pytest.raises(Exception):
            RunJsonpathQuery.main()
