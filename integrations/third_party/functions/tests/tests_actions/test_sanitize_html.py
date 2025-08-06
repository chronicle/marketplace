from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import SanitizeHTML

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestHtmlSanitize:
    @set_metadata(
        parameters={
            "Input HTML": "<b>bold</b><script>alert(1)</script>",
            "Tags": "b",
            "Attributes": "",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_tags_only(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "<script>" not in result
        assert "<b>bold</b>" in result
        assert "&lt;script&gt;" in result
        assert "alert(1)" in result

    @set_metadata(
        parameters={
            "Input HTML": '<p style="color:red;" onclick="alert(1)">Test</p>',
            "Tags": "p",
            "Attributes": "style",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_tags_styles_attributes(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "onclick" not in result
        assert 'style="color:red;"' in result
        assert result.startswith("<p")

    @set_metadata(
        parameters={
            "Input HTML": '<span style="font-weight:bold;color:blue">Text</span>',
            "Tags": "span",
            "Attributes": "style",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_tags_styles_attributes_partial_allowed(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "font-weight" not in result
        assert "color:blue" in result

    @set_metadata(
        parameters={
            "Input HTML": '<p style="color:blue; position:absolute;">Hello</p>',
            "Tags": "p",
            "Attributes": "style",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_tags_styles_attributes_partial_styles(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "color:blue" in result
        assert "position:absolute" not in result
        assert result.startswith("<p")

    @set_metadata(
        parameters={
            "Input HTML": '<img src="x.jpg" alt="Nice" onerror="alert(1)" data-test="123">',
            "Tags": "img",
            "Attributes": "src, alt",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_tags_and_attributes_no_styles(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert 'src="x.jpg"' in result
        assert 'alt="Nice"' in result
        assert "onerror" not in result
        assert "data-test" not in result

    @set_metadata(
        parameters={
            "Input HTML": '<div onclick="alert(123)" custom-attr="yes">Click here</div>',
            "Tags": "div",
            "Attributes": "",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "true",
            "Allow All Styles": "false",
        }
    )
    def test_tags_and_allow_all_attrs_and_not_styles(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "onclick" in result
        assert "custom-attr" in result
        assert "<div" in result

    @set_metadata(
        parameters={
            "Input HTML": '<div style="color:green;" title="info">Note</div>',
            "Tags": "",
            "Attributes": "style",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_styles_and_attributes_and_not_tags(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "color:green" in result

    @set_metadata(
        parameters={
            "Input HTML": '<span style="color:red;" data-x="1">Hi</span>',
            "Tags": "",
            "Attributes": "",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "true",
            "Allow All Styles": "false",
        }
    )
    def test_styles_and_allow_all_attrs_and_not_tags(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "style=" in result
        assert "data-x=" in result

    @set_metadata(
        parameters={
            "Input HTML": '<div style="color:red;">Hello</div>',
            "Tags": "",
            "Attributes": "",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_only_styles_set(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "color:red" in result

    @set_metadata(
        parameters={
            "Input HTML": '<button type="submit" onclick="doBadStuff()">Go</button>',
            "Tags": "button",
            "Attributes": "type",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_attributes_and_tags_and_not_styles(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert 'type="submit"' in result
        assert "onclick" not in result

    @set_metadata(
        parameters={
            "Input HTML": '<div style="color:green;" data-x="1">Text</div>',
            "Tags": "div",
            "Attributes": "",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "true",
            "Allow All Styles": "false",
        }
    )
    def test_styles_and_allow_all_attrs_and_tags(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "style=" in result
        assert "data-x=" in result
        assert result.startswith("<div")

    @set_metadata(
        parameters={
            "Input HTML": '<div style="color:blue;" title="info">Hello</div>',
            "Tags": "",
            "Attributes": "title",
            "Styles": "color",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_attributes_and_styles(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "color:blue" in result
        assert 'title="info"' in result

    @set_metadata(
        parameters={
            "Input HTML": '<button type="submit" onclick="alert(1)">Go</button>',
            "Tags": "",
            "Attributes": "type",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_only_attributes(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert 'type="submit"' in result
        assert "<button" not in result

    @set_metadata(
        parameters={
            "Input HTML": '<a href="x" data-x="y">Click</a>',
            "Tags": "",
            "Attributes": "",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "true",
            "Allow All Styles": "false",
        }
    )
    def test_only_allow_all_attrs(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "href=" in result
        assert "data-x=" in result

    @set_metadata(
        parameters={
            "Input HTML": '<script>alert("xss")</script><p onclick="x()">Text</p>',
            "Tags": "",
            "Attributes": "",
            "Styles": "",
            "Allow All Tags": "false",
            "Allow All Attributes": "false",
            "Allow All Styles": "false",
        }
    )
    def test_all_disabled_bleach_clean(self, action_output: MockActionOutput) -> None:
        SanitizeHTML.main()

        result = action_output.results.result_value
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert "&lt;script&gt;" in result
        assert "&lt;p" in result
        assert "onclick=" in result