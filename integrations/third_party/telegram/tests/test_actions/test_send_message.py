from __future__ import annotations

import unittest
import requests

from integration_testing.set_meta import set_metadata
from ..common import CONFIG_PATH
from ...actions import SendMessage

class TestSendMessageIntegration:
    BASE_URL = "http://localhost:8000"

    @set_metadata(
        parameters={
            "Message": "asd",
            "Chat ID": "1234"
        },
        integration_config_file_path=CONFIG_PATH
    )
    def test_send_message_success(self, script_session):
        payload = {
            "chat_id": 865157104,
            "text": "hi !"
        }

        SendMessage.main()

        assert len(script_session.request_history) == 1

    def test_send_message_missing_text(self):
        payload = {
            "chat_id": 865157104
            # text пропущен
        }

        response = requests.post(f"{self.BASE_URL}/send-message", json=payload)

        self.assertEqual(response.status_code, 400)

if __name__ == 'main':
    unittest.main()





























