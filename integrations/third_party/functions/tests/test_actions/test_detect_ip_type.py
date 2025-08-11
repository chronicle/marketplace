from __future__ import annotations

import pytest

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from actions import DetectIpType

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

DUMMY_CASE_ID = "case-123"
DUMMY_ALERT = {
    "identifier": "alert-123",
    "name": "Test Alert",
}


class TestDetectIpType:
    @set_metadata(
        parameters={"IP Addresses": "192.168.1.1"},
        input_context={"case": {"id": DUMMY_CASE_ID}, "alert": DUMMY_ALERT},
        entities=[]
    )
    def test_detect_ipv4_success(self, action_output: MockActionOutput) -> None:
        DetectIpType.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert "IPv4" in action_output.results.output_message

    @set_metadata(
        parameters={"IP Addresses": "2001:4860:4860::8888"},
        input_context={"case": {"id": DUMMY_CASE_ID}, "alert": DUMMY_ALERT},
        entities=[]
    )
    def test_detect_ipv6_success(self, action_output: MockActionOutput) -> None:
        DetectIpType.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert "IPv6" in action_output.results.output_message

    @set_metadata(
        parameters={"IP Addresses": "not.an.ip"},
        input_context={"case": {"id": DUMMY_CASE_ID}, "alert": DUMMY_ALERT},
        entities=[]
    )
    def test_detect_undetected_ip(self, action_output: MockActionOutput) -> None:
        DetectIpType.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert "UNDETECTED" in action_output.results.output_message

    @set_metadata(
        parameters={"IP Addresses": "192.168.1.1,not.an.ip,2001:4860:4860::8888"},
        input_context={"case": {"id": DUMMY_CASE_ID}, "alert": DUMMY_ALERT},
        entities=[]
    )
    def test_multiple_ip_types(self, action_output: MockActionOutput) -> None:
        DetectIpType.main()

        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.result_value is True
        assert "IPv4" in action_output.results.output_message
        assert "IPv6" in action_output.results.output_message
        assert "UNDETECTED" in action_output.results.output_message
