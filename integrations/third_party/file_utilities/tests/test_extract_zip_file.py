from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ..actions import ExtractZipFiles

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)


class TestFileUtilitiesInvalidParameters:
    @set_metadata(
        parameters={
            "Include Data In JSON Result": "False",
            "Create Entities": "True",
            "Zip File Password": "password123",
            "BruteForce Password": "False",
            "Add to Case Wall": "True",
            "Zip Password List Delimiter": ",",
            "File Format": "NotZip"
        }
    )
    def test_invalid_file_format_param(self, action_output: MockActionOutput) -> None:
        ExtractZipFiles.main()

        assert action_output.results.result_value == "false"
        assert action_output.results.execution_state == ExecutionState.FAILED

        # Проверка на наличие ошибки в output_message
        assert "File Format" in action_output.results.output_message
        assert "NotZip" in action_output.results.output_message

        # Убеждаемся, что валидные параметры не попали в сообщение об ошибке
        for correct_param in [
            "Include Data In JSON Result",
            "Create Entities",
            "Zip File Password",
            "BruteForce Password",
            "Add to Case Wall",
            "Zip Password List Delimiter",
        ]:
            assert correct_param not in action_output.results.output_message
