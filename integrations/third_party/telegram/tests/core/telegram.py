from __future__ import annotations

import dataclasses
from typing import Any

@dataclasses.dataclass
class Telegram:
    messages: list[dict[str, Any]] = dataclasses.field(default_factory=list)

    def add_message(self, message: dict[str, Any]):
        self.messages.append(message)

    def get_messages(self) -> list[dict[str, Any]]:
        return self.messages

    def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        message = {
            "chat_id": chat_id,
            "text": text,
        }
        self.add_message(message)
        return {"ok": True, "result": message}
