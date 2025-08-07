from __future__ import annotations

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from ..core.session import TelegramSession  # 👈 корректный импорт внутри tests

@set_metadata(integration_config_file_path="tests/integration_config.yaml")
def test_send_message_success(
    script_session: TelegramSession,
    action_output: MockActionOutput,
) -> None:
    response = script_session.get(
        "/bot123456:ABC/sendMessage",
        json={"chat_id": 1717760178, "text": "hi!"},
    )

    print("=== ✅ RAW RESPONSE ===")
    print(f"Status: {response.status_code}")
    print("Body:", response.text)
    print("=======================")

    assert response.status_code == 200 or response.status_code == 500
    result = response.json()

    assert result.get("ok"), f"❌ 'ok' not found or False. Full response: {result}"
    assert "message_id" in result, f"❌ 'message_id' missing in response: {result}"


@set_metadata(integration_config_file_path="tests/integration_config.yaml")
def test_send_message_missing_text(script_session: TelegramSession) -> None:
    response = script_session.get(
        "/bot123456:ABC/sendMessage",
        json={"chat_id": 1717760178},
    )

    print("=== ⚠️ RAW RESPONSE (missing text) ===")
    print(f"Status: {response.status_code}")
    print("Body:", response.text)
    print("======================================")

    assert response.status_code == 500
    assert "text" in response.text or "error" in response.text
