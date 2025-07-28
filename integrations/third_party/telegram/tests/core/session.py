from integration_testing.requests.session import MockSession
from integration_testing.requests.response import MockResponse
from integration_testing.custom_types import MockRequest
from packages.integration_testing.src.integration_testing import router
from ..core.product import Telegram
from typing import Any, Dict


class TelegramSession(MockSession[MockRequest, MockResponse, Telegram]):
    def get_routed_functions(self):
        return [
            self.send_message,
            self.get_me,
            self.get_chat,
            self.get_updates,
            self.send_document,
            self.send_location,
            self.send_photo,
            self.send_poll,
            self.set_chat_permissions,
            self.set_user_permissions,
        ]











    @router.get(r"/bot\S+/sendMessage")
    def send_message(self, request: MockRequest) -> MockResponse:
        response_json = self._product.send_message(
            chat_id=request.kwargs["params"]["chat_id"],
            text=request.kwargs["params"]["text"],
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/getMe")
    def get_me(self, request: MockRequest) -> MockResponse:
        response_json = self.product.test_connectivity()
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/getChat")
    def get_chat(self, request: MockRequest) -> MockResponse:
        response_json = self.product.get_chat_details(
            chat_id=request.kwargs["params"]["chat_id"]
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/getUpdates")
    def get_updates(self, request: MockRequest) -> MockResponse:
        response_json = self.product.get_messages(
            offset=request.kwargs["params"].get("offset"),
            allowed_updates=request.kwargs["params"].get("allowed_updates"),
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/sendDocument")
    def send_document(self, request: MockRequest) -> MockResponse:
        response_json = self.product.send_doc(
            chat_id=request.kwargs["params"]["chat_id"],
            doc_url=request.kwargs["params"]["document"],
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/sendLocation")
    def send_location(self, request: MockRequest) -> MockResponse:
        response_json = self.product.send_location(
            chat_id=request.kwargs["params"]["chat_id"],
            latitude=request.kwargs["params"]["latitude"],
            longitude=request.kwargs["params"]["longitude"],
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/sendPhoto")
    def send_photo(self, request: MockRequest) -> MockResponse:
        try:
            payload: Dict[str, Any] = get_request_payload(request)

            chat_id = payload["chat_id"]
            photo_url = payload["photo"]
            response_data = self._product.send_photo(chat_id, photo_url)
            return MockResponse(content=response_data)
        except Exception as e:
            return MockResponse(content=str(e), status_code=500)

    @router.get(r"/bot\S+/sendPoll")
    def send_poll(self, request: MockRequest) -> MockResponse:
        response_json = self.product.ask_question(
            chat_id=request.kwargs["params"]["chat_id"],
            question=request.kwargs["params"]["question"],
            options=request.kwargs["params"]["options"],
            is_anonymous=request.kwargs["params"]["is_anonymous"],
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/setChatPermissions")
    def set_chat_permissions(self, request: MockRequest) -> MockResponse:
        response_json = self.product.set_default_chat_permissions(
            chat_id=request.kwargs["params"]["chat_id"],
            can_send_polls=request.kwargs["params"]["can_send_polls"],
            can_pin_messages=request.kwargs["params"]["can_pin_messages"],
            can_invite_users=request.kwargs["params"]["can_invite_users"],
            can_change_info=request.kwargs["params"]["can_change_info"],
            can_post_messages=request.kwargs["params"]["can_post_messages"],
        )
        return self.create_json_response(response_json)

    @router.get(r"/bot\S+/setUserPermissions")
    def set_user_permissions(self, request: MockRequest) -> MockResponse:
        response_json = self.product.set_user_permissions(
            chat_id=request.kwargs["params"]["chat_id"],
            user_id=request.kwargs["params"]["user_id"],
            is_anonymous=request.kwargs["params"]["is_anonymous"],
            can_change_info=request.kwargs["params"]["can_change_info"],
            can_post_messages=request.kwargs["params"]["can_post_messages"],
            can_edit_messages=request.kwargs["params"]["can_edit_messages"],
            can_delete_messages=request.kwargs["params"]["can_delete_messages"],
            can_invite_users=request.kwargs["params"]["can_invite_users"],
            can_restrict_users=request.kwargs["params"]["can_restrict_users"],
            can_pin_messages=request.kwargs["params"]["can_pin_messages"],
            can_promote_members=request.kwargs["params"]["can_promote_members"],
        )
        return self.create_json_response(response_json)










