from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ...actions import IpToInteger

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

VALID_IPS = [
    ("8.8.8.8", 134744072),
    ("1.1.1.1", 16843009),
    ("0.0.0.0", 0)
]

class TestIpToLongFullCoverage:

    @set_metadata(parameters={"IP Addresses": "8.8.8.8"})
    def test_single_ip(self, action_output: MockActionOutput) -> None:
        IpToInteger.main()
        assert action_output.results.result_value == "134744072"
        assert action_output.results.json_output.json_result == {"8.8.8.8": 134744072}
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"IP Addresses": "8.8.8.8,1.1.1.1"})
    def test_multiple_ips(self, action_output: MockActionOutput) -> None:
        IpToInteger.main()
        expected = {"8.8.8.8": 134744072, "1.1.1.1": 16843009}
        expected_result = ",".join(str(v) for v in expected.values())
        assert action_output.results.result_value == expected_result
        assert action_output.results.json_output.json_result == expected
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"IP Addresses": "0.0.0.0"})
    def test_zero_ip(self, action_output: MockActionOutput) -> None:
        IpToInteger.main()
        assert action_output.results.result_value == "0"
        assert action_output.results.json_output.json_result == {"0.0.0.0": 0}
        assert action_output.results.execution_state is ExecutionState.COMPLETED


    @set_metadata(parameters={"IP Addresses": ""})
    def test_empty_ip(self, action_output: MockActionOutput) -> None:
        IpToInteger.main()
        assert action_output.results.result_value == ""
        assert action_output.results.json_output.json_result == {}
        assert action_output.results.execution_state is ExecutionState.COMPLETED
