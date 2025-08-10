from __future__ import annotations
import base64

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from integrations.third_party.file_utilities.actions.DecodeBase64 import main

pytest_plugins = ("integration_testing.conftest",)

class TestDecodeBase64:

    @set_metadata(parameters={"Base64 Input": base64.b64encode(b"hello utf8").decode(), "Encoding": "utf-8"})
    def test_decode_utf8(self, action_output: MockActionOutput) -> None:
        main()
        result = action_output.results.json_output.json_result
        assert result.get("decoded_content") == "hello utf8"
        assert action_output.results.execution_state == ExecutionState.COMPLETED

    @set_metadata(parameters={"Base64 Input": base64.b64encode(b"hello ascii").decode(), "Encoding": "ascii"})
    def test_decode_ascii(self, action_output: MockActionOutput) -> None:
        main()
        result = action_output.results.json_output.json_result
        assert result.get("decoded_content") == "hello ascii"
        assert action_output.results.execution_state == ExecutionState.COMPLETED
