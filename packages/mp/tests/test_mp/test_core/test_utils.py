# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import pytest

import mp.core.utils


@pytest.mark.parametrize(
    ("input_string", "expected_output"),
    [
        ("CamelCase", "camel_case"),
        ("snake_case", "snake_case"),
        ("camelCase123", "camel_case123"),
        ("Camel-Case", "camel_case"),
        ("Space Case", "space_case"),
        ("123Number", "123_number"),
        ("ALLCAPS", "allcaps"),
        ("alllower", "alllower"),
    ],
)
def test_str_to_snake_case(input_string: str, expected_output: str) -> None:
    assert mp.core.utils.str_to_snake_case(input_string) == expected_output


@pytest.mark.parametrize(
    ("input_string", "expected_output"),
    [
        (">=3.11", "3.11"),
        ("==3.7", "3.7"),
        ("~=3.12", "3.12"),
        ("!=3.13", "3.13"),
        ("<=2.7", "2.7"),
        ("<3.7", "3.7"),
        (">3.14", "3.14"),
        ("===1.0", "1.0"),
        ("==>2.0", "2.0"),
        ("==<3.0", "3.0"),
        ("!==4.0", "4.0"),
        (">=3.11,<3.13", "3.11"),
        ("<3.13,>=3.11", "3.11"),
        (">=3.11, <3.13", "3.11"),
        ("<3.13, >=3.11", "3.11"),
        ("==3.7, <3.13", "3.7"),
        (">3.7, <2.7", "2.7"),
    ],
)
def test_get_python_version_from_string(
    input_string: str,
    expected_output: str,
) -> None:
    assert (
        mp.core.utils.get_python_version_from_version_string(input_string)
        == expected_output
    )


class TestTrimValues:
    def test_string_below_limit(self) -> None:
        input_str = "Short string"
        assert mp.core.utils.trim_values(input_str) == input_str

    def test_string_at_limit(self) -> None:
        input_str = "x" * mp.core.utils.ERR_MSG_STRING_LIMIT
        assert mp.core.utils.trim_values(input_str) == input_str

    def test_string_at_limit_plus_padding(self) -> None:
        input_str = "x" * mp.core.utils.ERR_MSG_STRING_LIMIT
        assert mp.core.utils.trim_values(input_str) == input_str

    def test_string_exceeding_limit(self) -> None:
        input_str = "x" * (mp.core.utils.ERR_MSG_STRING_LIMIT + 10)
        result = mp.core.utils.trim_values(input_str)
        assert len(result) < len(input_str)
        assert mp.core.utils.TRIM_CHARS in result

    def test_empty_string(self) -> None:
        assert not mp.core.utils.trim_values("")

    def test_string_with_special_characters(self) -> None:
        special_chars = "Hello 🌍 こんにちは" * 50
        result = mp.core.utils.trim_values(special_chars)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(special_chars)

    def test_string_with_whitespace(self) -> None:
        whitespace_str = "    " * 100
        result = mp.core.utils.trim_values(whitespace_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(whitespace_str)

    def test_string_with_newlines(self) -> None:
        multiline_str = "Line\n" * 100
        result = mp.core.utils.trim_values(multiline_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(multiline_str)

    def test_unicode_characters(self) -> None:
        unicode_str = "🌍🌎🌏" * 100
        result = mp.core.utils.trim_values(unicode_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(unicode_str)

    def test_mixed_content_string(self) -> None:
        mixed_str = "Ab1!@#$%^&*()" * 50
        result = mp.core.utils.trim_values(mixed_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(mixed_str)

    def test_just_over_limit(self) -> None:
        input_str = "x" * (
            mp.core.utils.ERR_MSG_STRING_LIMIT + len(mp.core.utils.TRIM_CHARS) + 1
        )
        result = mp.core.utils.trim_values(input_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(input_str)

    def test_non_ascii_characters(self) -> None:
        non_ascii = "áéíóúñ" * 50
        result = mp.core.utils.trim_values(non_ascii)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) < len(non_ascii)

    def test_boundary_values(self) -> None:
        test_cases = [
            mp.core.utils.ERR_MSG_STRING_LIMIT - 1,
            mp.core.utils.ERR_MSG_STRING_LIMIT,
            mp.core.utils.ERR_MSG_STRING_LIMIT + 1,
        ]

        for length in test_cases:
            input_str = "x" * length
            result = mp.core.utils.trim_values(input_str)
            if length > mp.core.utils.ERR_MSG_STRING_LIMIT:
                assert mp.core.utils.TRIM_CHARS in result
                assert len(result) < len(input_str)
            else:
                assert result == input_str

    def test_very_long_string(self) -> None:
        input_str = "x" * (mp.core.utils.ERR_MSG_STRING_LIMIT * 1000)
        result = mp.core.utils.trim_values(input_str)
        assert len(result) < len(input_str)
        assert mp.core.utils.TRIM_CHARS in result
        assert len(result) == mp.core.utils.ERR_MSG_STRING_LIMIT

    @pytest.mark.parametrize(
        "input_str",
        [
            "x" * (mp.core.utils.ERR_MSG_STRING_LIMIT + 6),
            "Hello World" * 50,
            "🌍" * (mp.core.utils.ERR_MSG_STRING_LIMIT + 6),
            "    " * (mp.core.utils.ERR_MSG_STRING_LIMIT + 6),
            "\n" * (mp.core.utils.ERR_MSG_STRING_LIMIT + 6),
        ],
    )
    def test_various_inputs(self, input_str: str) -> None:
        result = mp.core.utils.trim_values(input_str)
        assert len(result) <= mp.core.utils.ERR_MSG_STRING_LIMIT
        if len(input_str) > mp.core.utils.ERR_MSG_STRING_LIMIT:
            assert mp.core.utils.TRIM_CHARS in result
