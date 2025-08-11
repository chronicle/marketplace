from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions.SpellCheckString import main

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

CORRECT_INPUT: str = "This sentence is correctly written"
INPUT_WITH_ERRORS: str = "Ths sentnce has erors"
EMPTY_INPUT: str = ""


class TestSpellCheckString:
    @set_metadata(parameters={"String": CORRECT_INPUT})
    def test_correct_input(self, action_output: MockActionOutput) -> None:
        main()

        json_result = action_output.results.json_output.json_result

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 100
        assert action_output.results.output_message == "The input string is 100% accurate"
        assert json_result["accuracy"] == 100
        assert json_result["total_misspelled_words"] == 0
        assert json_result["misspelled_words"] == []
        assert json_result["corrected_string"] == CORRECT_INPUT

    @set_metadata(parameters={"String": INPUT_WITH_ERRORS})
    def test_input_with_errors(self, action_output: MockActionOutput) -> None:
        main()

        json_result = action_output.results.json_output.json_result
        accuracy = json_result["accuracy"]

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert 0 < accuracy < 100
        assert json_result["total_misspelled_words"] > 0
        assert len(json_result["misspelled_words"]) == json_result["total_misspelled_words"]
        assert json_result["corrected_string"] != INPUT_WITH_ERRORS

    @set_metadata(parameters={"String": EMPTY_INPUT})
    def test_empty_input(self, action_output: MockActionOutput) -> None:
        main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 0
        assert action_output.results.output_message == "No input to test."
        assert action_output.results.json_output is None
