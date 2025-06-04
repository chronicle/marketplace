from __future__ import annotations

import dataclasses
from typing import Any

@dataclasses.dataclass
class Telegram:
    messages: list[dict[str, Any]] = dataclasses.field(default_factory=list)
    should_fail_next_call: bool = False
    _updates_response: dict | None = None

    def fail_next_call(self):
        self.should_fail_next_call = True

    def add_message(self, message: dict[str, Any]):
        self.messages.append(message)

    def get_messages(self) -> list[dict[str, Any]]:
        return self.messages

    def set_updates_response(self, response: dict):
        self._updates_response = response

    def send_message(self, chat_id: str, text: str) -> dict[str, Any]:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SendMessage")
        message = {
            "chat_id": chat_id,
            "text": text,
        }
        self.add_message(message)
        return {"ok": True, "result": message}

    def test_connectivity(self) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for GetBotDetails")
        return {"ok": True, "result": {"id": 123456789, "is_bot": True, "first_name": "test_bot", "username": "test_bot_username"}}

    def get_chat_details(self, chat_id: str) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure")
        return {
            "ok": True,
            "result": {
                "id": chat_id,
                "type": "channel",
                "title": "Test Chat",
                "invite_link": f"https://t.me/joinchat/test_invite_link_{chat_id}"
            }
        }

    def get_messages(self, offset: str | None, allowed_updates: str | None) -> dict:
        # Return pre-set updates response if available
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for GetMessages")

        if self._updates_response:
            return self._updates_response

        # Existing default behavior
        return {
            "ok": True,
            "result": [
                {
                    "update_id": 123456789,
                    "message": {
                        "message_id": 1,
                        "from": {"id": 987654321, "is_bot": False, "first_name": "User"},
                        "chat": {"id": 12345, "type": "private"},
                        "date": 1678886400,
                        "text": "Hello from Telegram!",
                    },
                }
            ],
        }


    def send_doc(self, chat_id: str, doc_url: str) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SendDocument")
        return {"ok": True, "result": {"chat_id": chat_id, "document_url": doc_url, "file_id": "test_file_id"}}

    def send_location(self, chat_id: str, latitude: str, longitude: str) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SendLocation")
        return {"ok": True, "result": {"chat_id": chat_id, "latitude": latitude, "longitude": longitude}}

    def send_photo(self, chat_id: str, photo_url: str) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SendPhoto")
        return {"ok": True, "result": {"chat_id": chat_id, "photo_url": photo_url}}

    def ask_question(self, chat_id: str, question: str, options: list[str], is_anonymous: bool) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SendPoll")
        return {"ok": True,
                "result": {"chat_id": chat_id, "question": question, "options": options, "is_anonymous": is_anonymous}}

    def set_default_chat_permissions(self, chat_id: str, can_send_polls: bool, can_pin_messages: bool,
                                     can_invite_users: bool, can_change_info: bool, can_post_messages: bool) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SetDefaultChatPermissions")
        return {"ok": True, "result": {"chat_id": chat_id, "permissions": {"can_send_polls": can_send_polls,
                                                                           "can_pin_messages": can_pin_messages,
                                                                           "can_invite_users": can_invite_users,
                                                                           "can_change_info": can_change_info,
                                                                           "can_post_messages": can_post_messages}}}

    def set_user_permissions(self, chat_id: str, user_id: str, is_anonymous: bool, can_change_info: bool,
                             can_post_messages: bool, can_edit_messages: bool, can_delete_messages: bool,
                             can_invite_users: bool, can_restrict_users: bool, can_pin_messages: bool,
                             can_promote_members: bool) -> dict:
        if self.should_fail_next_call:
            self.should_fail_next_call = False
            raise Exception("Simulated API failure for SetUserPermissions")
        return {"ok": True, "result": {"chat_id": chat_id, "user_id": user_id, "is_anonymous": is_anonymous,
                                       "can_change_info": can_change_info, "can_post_messages": can_post_messages,
                                       "can_edit_messages": can_edit_messages,
                                       "can_delete_messages": can_delete_messages, "can_invite_users": can_invite_users,
                                       "can_restrict_users": can_restrict_users, "can_pin_messages": can_pin_messages,
                                       "can_promote_members": can_promote_members}}
