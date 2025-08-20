from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import MathFunctions

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

DISPLAY_FN: str = "Display"
DISPLAY_INPUT: str = "1000"
EXPECTED_RESULT_DISPLAY: str = "1,000.0"

HEX_FN: str = "Hex"
HEX_INPUT: str = "1000"
EXPECTED_RESULT_HEX: str = "0x3e8"

MIN_FN: str = "Min"
MIN_INPUT: str = "5,7,9"
EXPECTED_RESULT_MIN: float = 5.0
EXPECTED_MESSAGE_MIN: str = "Min number in [5.0, 7.0, 9.0] is 5.0."

ROUND_FN: str = "Round"
ROUND_INPUT: str = "1.3, 2.1, 4.8"
EXPECTED_RESULT_ROUND: list[int] = [1, 2, 5]
EXPECTED_MESSAGE_ROUND: str = (
    f"[{ROUND_INPUT}] successfully converted to {EXPECTED_RESULT_ROUND} with round function"
)


class TestDisplayFormattedNumber:
    @set_metadata(parameters={"Numbers": DISPLAY_INPUT, "Function": DISPLAY_FN})
    def test_display_single_number_formatting(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        assert action_output.results.result_value == EXPECTED_RESULT_DISPLAY
        assert (
            action_output.results.output_message
            == f"Successfully converted [{float(DISPLAY_INPUT)}] to ['{EXPECTED_RESULT_DISPLAY}']"
        )
        assert action_output.results.json_output.json_result == [EXPECTED_RESULT_DISPLAY]
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestHexConversion:
    @set_metadata(parameters={"Numbers": HEX_INPUT, "Function": HEX_FN})
    def test_hex_single_number_conversion(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        assert action_output.results.result_value == EXPECTED_RESULT_HEX
        assert (
            action_output.results.output_message
            == f"[{float(HEX_INPUT)}] successfully converted to ['{EXPECTED_RESULT_HEX}'] with hex function"
        )
        assert action_output.results.json_output.json_result == [EXPECTED_RESULT_HEX]
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestMinFunction:
    @set_metadata(parameters={"Numbers": MIN_INPUT, "Function": MIN_FN})
    def test_min_function(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        assert action_output.results.result_value == EXPECTED_RESULT_MIN
        assert action_output.results.output_message == EXPECTED_MESSAGE_MIN
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestRoundFunction:
    @set_metadata(parameters={"Numbers": ROUND_INPUT, "Function": ROUND_FN})
    def test_round_function(self, action_output: MockActionOutput) -> None:
        MathFunctions.main()

        assert action_output.results.result_value is True
        assert action_output.results.output_message == EXPECTED_MESSAGE_ROUND
        assert action_output.results.json_output.json_result == EXPECTED_RESULT_ROUND
        assert action_output.results.execution_state is ExecutionState.COMPLETED

