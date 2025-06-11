from __future__ import annotations

import contextlib
import dataclasses

from TIPCommon.types import SingleJson


@dataclasses.dataclass(slots=True)
class Telegram:
    messages: list[SingleJson] = dataclasses.field(default_factory=list)
    _updates_response: SingleJson | None = None
    _chat_details: SingleJson | None = None
    _bot_details: SingleJson | None = None
    _send_doc_response: SingleJson | None = None
    _send_location_response: SingleJson | None = None
    _send_photo_response: SingleJson | None = None
    _ask_question_response: SingleJson | None = None
    _set_default_chat_permissions_response: SingleJson | None = None
    _set_user_permissions_response: SingleJson | None = None
    _fail_requests_active: bool = False

    @contextlib.contextmanager
    def fail_requests(self):
        self._fail_requests_active = True
        try:
            yield
        finally:
            self._fail_requests_active = False

    def add_message(self, message: SingleJson):
        self.messages.append(message)

    def set_updates_response(self, response: SingleJson):
        self._updates_response = response

    def set_chat_details(self, response: SingleJson):
        self._chat_details = response

    def set_bot_details(self, response: SingleJson):
        self._bot_details = response

    def set_send_doc_response(self, response: SingleJson):
        self._send_doc_response = response

    def set_send_location_response(self, response: SingleJson):
        self._send_location_response = response

    def set_send_photo_response(self, response: SingleJson):
        self._send_photo_response = response

    def set_ask_question_response(self, response: SingleJson):
        self._ask_question_response = response

    def set_set_default_chat_permissions_response(self, response: SingleJson):
        self._set_default_chat_permissions_response = response

    def set_set_user_permissions_response(self, response: SingleJson):
        self._set_user_permissions_response = response

    def send_message(self, chat_id: str, text: str) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for SendMessage")
        message = {
            "chat_id": chat_id,
            "text": text,
        }
        self.add_message(message)
        return {"ok": True, "result": message}

    def test_connectivity(self) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for GetBotDetails")

        if self._bot_details:
            return self._bot_details

        return {
            "ok": True,
            "result": {
                "id": 123456789,
                "is_bot": True,
                "first_name": "test_bot",
                "username": "test_bot_username",
            },
        }

    def get_chat_details(self, chat_id: str) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure")

        if self._chat_details:
            return self._chat_details

        return {
            "ok": True,
            "result": {
                "id": chat_id,
                "type": "channel",
                "title": "Test Chat",
                "invite_link": f"https://t.me/joinchat/test_invite_link_{chat_id}",
            },
        }

    def get_messages(
        self, offset: str | None, allowed_updates: str | None
    ) -> SingleJson:
        # Return pre-set updates response if available
        if self._fail_requests_active:
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
                        "from": {
                            "id": 987654321,
                            "is_bot": False,
                            "first_name": "User",
                        },
                        "chat": {"id": 12345, "type": "private"},
                        "date": 1678886400,
                        "text": "Hello from Telegram!",
                    },
                }
            ],
        }

    def send_doc(self, chat_id: str, doc_url: str) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for SendDocument")
        if self._send_doc_response:
            return self._send_doc_response
        return {
            "ok": True,
            "result": {
                "chat_id": chat_id,
                "document_url": doc_url,
                "file_id": "test_file_id",
            },
        }

    def send_location(self, chat_id: str, latitude: str, longitude: str) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Mock API failure")

        if self._send_location_response:
            return self._send_location_response

        return {
            "ok": True,
            "result": {
                "chat_id": chat_id,
                "latitude": latitude,
                "longitude": longitude,
            },
        }

    def send_photo(self, chat_id: str, photo_url: str) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for SendPhoto")
        if self._send_photo_response:
            return self._send_photo_response
        return {"ok": True, "result": {"chat_id": chat_id, "photo_url": photo_url}}

    def ask_question(
        self, chat_id: str, question: str, options: list[str], is_anonymous: bool
    ) -> SingleJson:

        if self._fail_requests_active:
            raise Exception("Simulated API failure for SendPoll")

        if self._ask_question_response:
            return self._ask_question_response

        return {
            "ok": True,
            "result": {
                "chat_id": chat_id,
                "question": question,
                "options": options,
                "is_anonymous": is_anonymous,
            },
        }

    def set_default_chat_permissions(
        self,
        chat_id: str,
        can_send_polls: bool,
        can_pin_messages: bool,
        can_invite_users: bool,
        can_change_info: bool,
        can_post_messages: bool,
    ) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for SetDefaultChatPermissions")
        if self._set_default_chat_permissions_response:
            return self._set_default_chat_permissions_response
        return {
            "ok": True,
            "result": {
                "chat_id": chat_id,
                "permissions": {
                    "can_send_polls": can_send_polls,
                    "can_pin_messages": can_pin_messages,
                    "can_invite_users": can_invite_users,
                    "can_change_info": can_change_info,
                    "can_post_messages": can_post_messages,
                },
            },
        }

    def set_user_permissions(
        self,
        chat_id: str,
        user_id: str,
        is_anonymous: bool,
        can_change_info: bool,
        can_post_messages: bool,
        can_edit_messages: bool,
        can_delete_messages: bool,
        can_invite_users: bool,
        can_restrict_users: bool,
        can_pin_messages: bool,
        can_promote_members: bool,
    ) -> SingleJson:
        if self._fail_requests_active:
            raise Exception("Simulated API failure for SetUserPermissions")
        if self._set_user_permissions_response:
            return self._set_user_permissions_response
        return {
            "ok": True,
            "result": {
                "chat_id": chat_id,
                "user_id": user_id,
                "is_anonymous": is_anonymous,
                "can_change_info": can_change_info,
                "can_post_messages": can_post_messages,
                "can_edit_messages": can_edit_messages,
                "can_delete_messages": can_delete_messages,
                "can_invite_users": can_invite_users,
                "can_restrict_users": can_restrict_users,
                "can_pin_messages": can_pin_messages,
                "can_promote_members": can_promote_members,
            },
        }
