import base64
import os
from unittest import mock
from integration_testing.set_meta import set_metadata
from integration_testing.platform.script_output import MockActionOutput
from integrations.third_party.file_utilities.actions import SaveBase64ToFile

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

class TestSaveBase64ToFile:
    @set_metadata(parameters={
        "Base64 Input": base64.b64encode(b"hello world").decode("utf-8"),
        "Filename": "test_file.txt",
        "File Extension": "",
        "Output Directory": "/tmp"
    })
    def test_save_base64_to_file(self, tmp_path, action_output: MockActionOutput):
        with mock.patch(
            "integrations.third_party.file_utilities.actions.SaveBase64ToFile.SiemplifyAction"
        ) as mock_siemplify:
            instance = mock_siemplify.return_value
            instance.parameters = {
                "Base64 Input": base64.b64encode(b"hello world").decode("utf-8"),
                "Filename": "test_file.txt",
                "File Extension": "",
            }
            instance.RUN_FOLDER = str(tmp_path)
            instance.is_remote = False
            instance.LOGGER = mock.Mock()
            instance.result = mock.Mock()
            instance.result.add_result_json = mock.Mock()
            instance.end = mock.Mock()

            SaveBase64ToFile.main()

            file_path = os.path.join(tmp_path, "downloads", "test_file.txt")
            assert os.path.isfile(file_path), "Файл не был создан"
            with open(file_path, "rb") as f:
                assert f.read() == b"hello world"
            assert instance.result.add_result_json.called
            instance.end.assert_called()
