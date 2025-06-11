from __future__ import annotations

from TIPCommon.base.action import ExecutionState
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata

from ..common import CONFIG_PATH
from ..core.session import TelegramSession
from ...actions import SendDocument


class TestSendDocument:
    CHAT_ID = "123456789"
    DOCUMENT_URL = "http://example.com/document.pdf"

    @set_metadata(
        parameters={"Chat ID": CHAT_ID, "Document URL": DOCUMENT_URL},
        integration_config_file_path=CONFIG_PATH,
    )
    def test_send_document_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SendDocument.main()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/sendDocument")
        assert request.kwargs["params"] == {
            "chat_id": self.CHAT_ID,
            "document": self.DOCUMENT_URL,
        }

        assert (
            action_output.results.output_message == "The document was sent successfully"
        )
        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert action_output.results.json_output.json_result == {
            "ok": True,
            "result": {
                "chat_id": self.CHAT_ID,
                "document_url": self.DOCUMENT_URL,
                "file_id": "test_file_id",
            },
        }
