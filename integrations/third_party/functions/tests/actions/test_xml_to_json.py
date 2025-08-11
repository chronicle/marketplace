from __future__ import annotations
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from actions import XMLtoJson

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest")


class TestXMLtoJson:
    @set_metadata(parameters={
        "xml": "<e><a>text</a><a>text</a></e>"
    })
    def test_successful_conversion_with_multiple_nodes(self, action_output: MockActionOutput) -> None:
        XMLtoJson.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert "e" in action_output.results.json_output.json_result
        assert action_output.results.json_output.json_result["e"]["a"] == ["text", "text"]
        assert action_output.results.json_output is not None

    @set_metadata(parameters={
        "xml": "<root><item>Value</item></root>"
    })
    def test_successful_single_node(self, action_output: MockActionOutput) -> None:
        XMLtoJson.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert action_output.results.json_output.json_result["root"]["item"] == "Value"
        assert action_output.results.json_output is not None

    @set_metadata(parameters={
        "xml": "<root><item>Value</item>"
    })
    def test_invalid_xml_failure(self, action_output: MockActionOutput) -> None:
        XMLtoJson.main()
        assert action_output.results.execution_state is ExecutionState.FAILED
        assert action_output.results.result_value is False
        assert "error" in action_output.results.output_message.lower()
        assert action_output.results.json_output is None

    @set_metadata(parameters={
        "xml": ""
    })
    def test_empty_input_failure(self, action_output: MockActionOutput) -> None:
        XMLtoJson.main()
        assert action_output.results.execution_state is ExecutionState.FAILED
        assert action_output.results.result_value is False
        assert "error" in action_output.results.output_message.lower()
        assert action_output.results.json_output is None
