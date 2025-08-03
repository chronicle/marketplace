from __future__ import annotations
from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from ...actions import ExtractIocs

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

IOC_STRING = "IP: 1.1.1.1, URL: http://test.com, Email: user@test.com"
NO_IOC_STRING = "Nothing useful here."
INVALID_IOC_STRING = "###$$$%%%&&&"
EMPTY_INPUT_STRING = ""

class TestExtractIocs:
    @set_metadata(
        parameters={
            "Input String": IOC_STRING,
        }
    )
    def test_extract_iocs_success(self, action_output: MockActionOutput) -> None:
        ExtractIocs.main()
        results = action_output.results

        assert results.execution_state == ExecutionState.COMPLETED
        json_result = results.json_output.json_result
        assert isinstance(json_result, dict)
        assert json_result.get("domains") == ["test.com"]
        assert json_result.get("ips") == ["1.1.1.1"]
        assert json_result.get("urls") == ["http://test.com"]
        assert json_result.get("emails") == ["user@test.com"]
        assert "extracted the following" in results.output_message.lower()
        assert results.output_message.strip() != ""

    @set_metadata(
        parameters={
            "Input String": NO_IOC_STRING,
        }
    )
    def test_extract_iocs_with_no_iocs(self, action_output: MockActionOutput) -> None:
        ExtractIocs.main()
        results = action_output.results
        assert results.execution_state == ExecutionState.COMPLETED
        json_result = results.json_output.json_result
        assert isinstance(json_result, dict)
        for key in ["domains", "ips", "urls", "emails"]:
            assert json_result.get(key) == []

        assert "no iocs extracted" in results.output_message.lower()
        assert results.output_message.strip() != ""

    @set_metadata(
        parameters={
            "Input String": EMPTY_INPUT_STRING,
        }
    )
    def test_extract_iocs_with_empty_input(self, action_output: MockActionOutput) -> None:
        ExtractIocs.main()
        results = action_output.results
        assert results.execution_state == ExecutionState.FAILED
        assert isinstance(results.output_message, str)
        assert "error" in results.output_message.lower()
        assert results.output_message.strip() != ""

    @set_metadata(
        parameters={
            "Input String": INVALID_IOC_STRING,
        }
    )
    def test_extract_iocs_with_invalid_input(self, action_output: MockActionOutput) -> None:
        ExtractIocs.main()
        results = action_output.results
        assert results.execution_state == ExecutionState.COMPLETED
        json_result = results.json_output.json_result
        assert isinstance(json_result, dict)
        for key in ["domains", "ips", "urls", "emails"]:
            assert json_result.get(key) == []
        assert "no iocs extracted" in results.output_message.lower()
        assert results.output_message.strip() != ""
