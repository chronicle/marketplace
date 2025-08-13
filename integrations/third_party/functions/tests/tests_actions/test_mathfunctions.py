from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import MathFunctions

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

NUMBERS_CSV_STR: str = "-1,-2.5,3"
ABS_FUNCTION: str = "Abs"
FLOAT_FUNCTION: str = "Float"


def float_list_str(lst):
    return "[" + ", ".join(f"{float(x)}" for x in lst) + "]"


class TestAbsFunction:
    @set_metadata(parameters={"Numbers": NUMBERS_CSV_STR, "Function": ABS_FUNCTION})
    def test_abs_conversion(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [-1.0, -2.5, 3.0]
        expected_abs = [abs(n) for n in expected_numbers]

        assert action_output.results.result_value is True
        assert (
            action_output.results.output_message
            == f"{float_list_str(expected_numbers)} successfully converted to {float_list_str(expected_abs)} with abs function"
        )
        assert action_output.results.json_output.json_result == expected_abs
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestFloatFunction:
    @set_metadata(parameters={"Numbers": NUMBERS_CSV_STR, "Function": FLOAT_FUNCTION})
    def test_float_conversion(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [-1.0, -2.5, 3.0]
        expected_float = [float(n) for n in expected_numbers]

        assert action_output.results.result_value is True
        assert (
            action_output.results.output_message
            == f"{float_list_str(expected_numbers)} successfully converted to {float_list_str(expected_float)} with float function"
        )
        assert action_output.results.json_output.json_result == expected_float
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestIntFunction:
    @set_metadata(
        parameters={
            "Numbers": "1.2,3.8,-4.9",
            "Function": "Int",
        }
    )
    def test_int_conversion(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [1.2,3.8,-4.9]
        expected_ints = [int(n) for n in expected_numbers]

        assert action_output.results.result_value is True
        assert (
            action_output.results.output_message
            == f"{expected_numbers} successfully converted to {expected_ints} with int function"
        )
        assert action_output.results.json_output.json_result == expected_ints
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestMaxFunction:
    @set_metadata(
        parameters={
            "Numbers": "10,-25,7",
            "Function": "Max",
        }
    )
    def test_max_function(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [10.0, -25.0, 7.0]
        max_number = max(expected_numbers)

        assert action_output.results.result_value == max_number
        assert action_output.results.output_message == f"Max number in {expected_numbers} is {max_number}."
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestSortFunction:
    @set_metadata(
        parameters={
            "Numbers": "3,1,2",
            "Function": "Sort",
        }
    )
    def test_sort_function(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [3.0, 1.0, 2.0]
        expected_sorted = sorted(expected_numbers)

        assert action_output.results.result_value is True
        assert (
            action_output.results.output_message
            == f"{expected_numbers} successfully converted to {expected_sorted} with sorted function"
        )
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestSumFunction:
    @set_metadata(
        parameters={
            "Numbers": "3,1,2",
            "Function": "Sum",
        }
    )
    def test_sum_function(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        expected_numbers = [3.0, 1.0, 2.0]
        expected_sum = sum(expected_numbers)

        assert action_output.results.result_value == expected_sum
        assert (
            action_output.results.output_message
            == f"Sum of array {expected_numbers} is {expected_sum}."
        )
        assert action_output.results.execution_state is ExecutionState.COMPLETED

