from __future__ import annotations

import os

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ..actions import GetFilesAsBase64

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_FILE = os.path.join(BASE_DIR, "testText.exe")
TXT_FILE = os.path.join(BASE_DIR, "testText.txt")


class TestFileTypeDetection:

    @set_metadata(parameters={"File Paths": EXE_FILE})
    def test_detect_file_type_exe(self, action_output: MockActionOutput) -> None:
        GetFilesAsBase64.main()

        print(action_output.results)

        result = action_output.results.json_output.json_result
        assert EXE_FILE in result["filenames"]
        assert len(result["data"]) == 1
        assert isinstance(result["data"][0], dict)
        assert isinstance(result["data"][0].get("base64"), str)

        assert action_output.results.output_message.startswith("Converted Files to Base64")
        assert action_output.results.execution_state is ExecutionState.COMPLETED

    @set_metadata(parameters={"File Paths": TXT_FILE})
    def test_detect_file_type_txt(self, action_output: MockActionOutput) -> None:
        GetFilesAsBase64.main()

        print(action_output.results)

        result = action_output.results.json_output.json_result
        assert TXT_FILE in result["filenames"]
        assert len(result["data"]) == 1
        assert isinstance(result["data"][0], dict)
        assert isinstance(result["data"][0].get("base64"), str)

        assert action_output.results.output_message.startswith("Converted Files to Base64")
        assert action_output.results.execution_state is ExecutionState.COMPLETED
