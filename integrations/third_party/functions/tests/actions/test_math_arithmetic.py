from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from actions import MathArithmetic


pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestMathArithmetic:
    @set_metadata(parameters={"Function": "Plus", "Arg 1": "5", "Arg 2": "7"})
    def test_plus_success(self, action_output: MockActionOutput) -> None:
        MathArithmetic.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 12
        assert action_output.results.output_message == "5 + 7 = 12"
        assert action_output.results.json_output is None

    @set_metadata(parameters={"Function": "Sub", "Arg 1": "10", "Arg 2": "4"})
    def test_sub_success(self, action_output: MockActionOutput) -> None:
        MathArithmetic.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 6
        assert action_output.results.output_message == "10 - 4 = 6"
        assert action_output.results.json_output is None

    @set_metadata(parameters={"Function": "Multi", "Arg 1": "3", "Arg 2": "7"})
    def test_multi_success(self, action_output: MockActionOutput) -> None:
        MathArithmetic.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 21
        assert action_output.results.output_message == "3 * 7 = 21"
        assert action_output.results.json_output is None

    @set_metadata(parameters={"Function": "Div", "Arg 1": "10", "Arg 2": "2"})
    def test_div_success(self, action_output: MockActionOutput) -> None:
        MathArithmetic.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 5
        assert action_output.results.output_message == "10 / 2 = 5.0"
        assert action_output.results.json_output is None

    @set_metadata(parameters={"Function": "Mod", "Arg 1": "10", "Arg 2": "3"})
    def test_mod_success(self, action_output: MockActionOutput) -> None:
        MathArithmetic.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value == 1
        assert action_output.results.output_message == "10 % 3 = 1"
        assert action_output.results.json_output is None
