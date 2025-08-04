from __future__ import annotations

import base64

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from actions import CreateThumbnail

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

IMAGE_PATH: str = "C:/Users/elgin/marketplace/integrations/third_party/functions/tests/actions/resources/test_image.jpg"
THUMBNAIL_SIZE: str = "100,100"


class TestCreateThumbnail:
    @set_metadata(
        parameters={
            "Base64 Image": base64.b64encode(open(IMAGE_PATH, "rb").read()).decode("utf-8"),
            "Thumbnail Size": THUMBNAIL_SIZE,
            "Input JSON": "",
            "Image Key Path": "",
        }
    )
    def test_create_thumbnail_success(self, action_output: MockActionOutput) -> None:
        CreateThumbnail.main()

        result = action_output.results.result_value
        output_msg = action_output.results.output_message
        execution_state = action_output.results.execution_state


        assert result is None
        assert "output message" in output_msg
        assert execution_state.name == "COMPLETED"

