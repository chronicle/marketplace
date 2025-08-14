from __future__ import annotations

from ast import Param

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import StringFunctions

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)
ALL_CAPS_STR: str = "ASD"
ALL_LOWER_STR: str = ALL_CAPS_STR.lower()
STRING_WITH_SPACES: str = "    asd    "
ONLY_SPACES: str = "       "
ALL_UPPER_STR: str = ALL_CAPS_STR.upper()
TITLE_STR: str = "Asd"
REPLACE_STR: str = "Abc"
EXPECTED_RESULT: str = "Abd"
COUNT_STR: str = "Parasocial"
EXPECTED_RESULT_COUNT: int = 3
FIND_STR: str = "Summer_ship 2025"
EXPECTED_RESULT_FIND: int = 9
REMOVE_NEW_LINES_STR: str = "Line1\nLine2"
EXPECTED_RESULT_REMOVE_NEW_LINES: str = "Line1 Line2"
IS_ALPHA_STR: str = "Alpha123"
EXPECTED_RESULT_IS_ALPHA: int = False
IS_DIGIT_STR: str = "012345678A"
EXPECTED_RESULT_IS_DIGIT: int = False
REGEX_REPLACE_STR: str = "Text me at 055 555 7777"
EXPECTED_RESULT_REGEX_REPLACE: str = "Text me at *** *** ****"
JSON_SERIALIZE_STR = [10, 20, 30]
EXPECTED_RESULT_JSON = '[10, 20, 30]'
REGEX_STR: str = "My numbers are 123 and 456 and 789"
EXPECTED_RESULT_REGEX: str = "123, 456, 789"
DECODE_BASE64_STR: str = "c3VtbWVyc2hpcCAyMDI1"
EXPECTED_RESULT_DECODE_BASE64: str = "summership 2025"
LOGIC_OPERATORS_STR: str = "A,B,C"
EXPECTED_RESULT_LOGIC_OPERATORS: str = "A AND B AND C"
SPLIT_STR: str = "A|B|C"
EXPECTED_RESULT_SPLIT: str = "['A', 'B', 'C']"






class TestStringToLower:
    LOWER_FN: str = "Lower"

    @set_metadata(parameters={"Input": ALL_CAPS_STR, "Function": LOWER_FN})
    def test_string_lower_on_upper_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == ALL_LOWER_STR
        assert (
                action_output.results.output_message
                == f"{ALL_CAPS_STR} successfully converted to {ALL_LOWER_STR} with lower function"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"Input": ALL_LOWER_STR, "Function": "Lower"})
    def test_string_lower_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == ALL_LOWER_STR
        assert (
                action_output.results.output_message
                == f"{ALL_LOWER_STR} successfully converted to {ALL_LOWER_STR} with lower function"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestStripString:
    STRIP_FN: str = "Strip"

    @set_metadata(parameters={"Input": STRING_WITH_SPACES, "Function": STRIP_FN})
    def test_strip_string_on_string_with_spaces(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == STRING_WITH_SPACES.strip()
        assert (
                action_output.results.output_message
                == f"{STRING_WITH_SPACES} successfully stripped with strip function"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"Input": ONLY_SPACES, "Function": STRIP_FN})
    def test_strip_string_on_empty_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == ONLY_SPACES.strip()
        assert (
                action_output.results.output_message
                == f"{ONLY_SPACES} successfully converted to {ONLY_SPACES.strip()} with strip function"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestStringToUpper:
    UPPER_FN: str = "Upper"

    @set_metadata(parameters={"Input": ALL_UPPER_STR,"Function": UPPER_FN})
    def test_string_upper_on_upper_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == ALL_UPPER_STR
        assert (
                action_output.results.output_message
                == f"{ALL_UPPER_STR} successfully converted to {ALL_UPPER_STR.upper()} with upper function"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


    @set_metadata(parameters={"Input": ALL_LOWER_STR,"Function": UPPER_FN})
    def test_string_upper_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == ALL_UPPER_STR
        assert (
                action_output.results.output_message
                == f"{ALL_LOWER_STR} successfully converted to {ALL_UPPER_STR} with upper function"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED



class TestTitleString:
    TITLE_FN: str = "Title"

    @set_metadata(parameters={"Input": ALL_LOWER_STR,"Function": TITLE_FN})
    def test_string_title_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == TITLE_STR
        assert (
                action_output.results.output_message
                == f"{ALL_LOWER_STR} successfully converted to {TITLE_STR} with title function"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED



class TestReplaceString:
    REPLACE_FN: str = "Replace"

    @set_metadata(parameters={
        "Input": REPLACE_STR,
        "Function": REPLACE_FN,
        "Param 1": "c",
        "Param 2": "d"
    })
    def test_string_replace_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT
        assert (
                action_output.results.output_message
                == f"{REPLACE_STR} successfully converted to {EXPECTED_RESULT} with replace function"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestCountString:
    COUNT_FN: str = "Count"

    @set_metadata(parameters={
        "Input": COUNT_STR,
        "Function": COUNT_FN,
        "Param 1": 'a'
    })
    def test_string_count_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_COUNT
        assert (
                action_output.results.output_message
                == f"'a' was found {EXPECTED_RESULT_COUNT} times in '{COUNT_STR}'"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestFindString:
    FIND_FN: str = "Find"

    @set_metadata(parameters={
        "Input": FIND_STR,
        "Function": FIND_FN,
        "Param 1": "i"
    })
    def test_string_find_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_FIND
        assert (
                action_output.results.output_message
                == f"'i' was found at index {EXPECTED_RESULT_FIND} in '{FIND_STR}'"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestRemoveNewLines:
    REMOVE_NEW_LINES_FN: str = "RemoveNewLines"

    @set_metadata(parameters={
        "Input": REMOVE_NEW_LINES_STR,
        "Function": REMOVE_NEW_LINES_FN
    })
    def test_string_remove_new_lines_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_REMOVE_NEW_LINES
        assert (
                action_output.results.output_message
                == f"{REMOVE_NEW_LINES_STR} successfully removed new lines: {EXPECTED_RESULT_REMOVE_NEW_LINES}"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

class TestIsAlpha:
    IS_ALPHA_FN: str = "IsAlpha"
    @set_metadata(parameters={
        "Input": IS_ALPHA_STR,
        "Function": IS_ALPHA_FN
    })
    def test_string_is_alpha_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_IS_ALPHA
        assert (
            action_output.results.output_message
            if f"All characters in {IS_ALPHA_STR} are alphanumeric"

            else  f"Not all characters in {IS_ALPHA_STR} are alphanumeric"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED



class TestIsDigit:
    IS_DIGIT_FN: str = "IsDigit"
    @set_metadata(parameters={
        "Input": IS_DIGIT_STR,
        "Function": IS_DIGIT_FN
    })
    def test_string_is_digit_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_IS_DIGIT
        assert (
            action_output.results.output_message
            if
            f"All characters in {IS_DIGIT_STR} are digits"
            else
            f"Not all characters in {IS_DIGIT_STR} are digits"

        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestRegexReplace:
    REGEX_REPLACE_FN: str = "Regex Replace"
    @set_metadata(parameters={
        "Input": REGEX_REPLACE_STR,
        "Function": REGEX_REPLACE_FN,
        "Param 1":  "\d",
        "Param 2": "*"
    })
    def test_string_regex_replace_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_REGEX
        assert (
                action_output.results.output_message
                == f"{REGEX_STR} successfully converted to {EXPECTED_RESULT_REGEX} with regex replace function"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED



class TestJSONSerialize:
    JSON_SERIALIZE_FN: str = "JSON Serialize"
    @set_metadata(parameters={
        "Input": JSON_SERIALIZE_STR,
        "Function": JSON_SERIALIZE_FN
    })
    def test_string_json_serialize_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_JSON
        assert (
                action_output.results.output_message
                ==  f"{JSON_SERIALIZE_STR} successfully serialized to JSON format"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED


class TestRegex:
    REGEX_FN: str = "Regex"
    @set_metadata(parameters={
        "Input": REGEX_STR,
        "Function": REGEX_FN,
        "Param 1": r"\d+",
        "Param 2": ""
    })
    def test_string_regex_replace_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_REGEX
        assert (
                action_output.results.output_message
                == f"Found following values:\n{EXPECTED_RESULT_REGEX}"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED



class TestDecodeBase64:
    DECODE_BASE_64_FN: str = "DecodeBase64"
    @set_metadata(parameters={
        "Input": DECODE_BASE64_STR,
        "Function": DECODE_BASE_64_FN,
        "Param 1": "UTF-8"

    })
    def test_string_decode_base64_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()
        assert action_output.results.result_value == EXPECTED_RESULT_DECODE_BASE64
        assert (
                action_output.results.output_message
                ==  f"Decoded base64 string to: {EXPECTED_RESULT_DECODE_BASE64}"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state is ExecutionState.COMPLETED

class TestEncodeBase64:
    ENCODE_BASE_64_FN: str = "EncodeBase64"
    ENCODE_BASE_64_STR: str = "summership 2025"
    EXPECTED_RESULT_ENCODE_BASE64: str = "c3VtbWVyc2hpcCAyMDI1"

    @set_metadata(parameters={
        "Input": ENCODE_BASE_64_STR,
        "Function": ENCODE_BASE_64_FN,
        "Param 1": "UTF-8"
    })
    def test_string_encode_base64_on_lower_string(self, action_output: MockActionOutput) -> None:
        StringFunctions.main()

        assert action_output.results.result_value == self.EXPECTED_RESULT_ENCODE_BASE64
        assert (
                action_output.results.output_message
                == f"Successfully base64 encoded {self.ENCODE_BASE_64_STR}."
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state == ExecutionState.COMPLETED

class TestLogicOperators:
    LOGIC_OPERATORS_FN: str = "LogicOperators"

    @set_metadata(parameters={
        "Input": LOGIC_OPERATORS_STR,
        "Function": LOGIC_OPERATORS_FN,
        "Param 1": "AND",
        "Param 2": ","
    })
    def test_string_logic_operators_on_lower_string(self, action_output: MockActionOutput) -> None:
        # Act
        StringFunctions.main()

        # Assert
        assert action_output.results.result_value == EXPECTED_RESULT_LOGIC_OPERATORS
        assert (
                action_output.results.output_message
                == f"{LOGIC_OPERATORS_STR} successfully converted to: {EXPECTED_RESULT_LOGIC_OPERATORS}"
        )
        assert action_output.results.json_output is None
        assert action_output.results.execution_state == ExecutionState.COMPLETED

class TestSplit:
    SPLIT_FN: str = "Split"

    @set_metadata(parameters={
        "Input": SPLIT_STR,
        "Function": SPLIT_FN,
        "Param 1": "|"
    })
    def test_string_split_with_param(self, action_output: MockActionOutput) -> None:
        # Act
        StringFunctions.main()

        # Assert
        assert action_output.results.result_value == EXPECTED_RESULT_SPLIT
        assert (
                action_output.results.output_message
                == f'Successfully split string {SPLIT_STR} with delimiter "|"'
        )
        assert action_output.results.execution_state == ExecutionState.COMPLETED