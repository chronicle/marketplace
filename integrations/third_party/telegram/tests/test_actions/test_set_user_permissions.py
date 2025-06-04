from __future__ import annotations

from integrations.third_party.telegram.actions.SetUserPermissions import main as SetUserPermissions
from integrations.third_party.telegram.tests.common import CONFIG_PATH
from integrations.third_party.telegram.tests.core.session import TelegramSession
from integrations.third_party.telegram.tests.core.telegram import Telegram
from packages.integration_testing.src.integration_testing.platform.external_context import MockExternalContext
from packages.integration_testing.src.integration_testing.platform.script_output import MockActionOutput
from packages.integration_testing.src.integration_testing.set_meta import set_metadata
from TIPCommon.base.action import ExecutionState


class TestSetUserPermissions:
    CHAT_ID = "123456789"
    USER_ID = "987654321"
    IS_ANONYMOUS = "True"
    CAN_EDIT_INFO = "False"
    CAN_POST_MESSAGES = "True"
    CAN_EDIT_MESSAGES = "False"
    CAN_DELETE_MESSAGES = "True"
    CAN_INVITE_USERS = "False"
    CAN_RESTRICT_USERS = "True"
    CAN_PROMOTE_MEMBERS = "False"
    CAN_PIN_MESSAGES = "True"

    @set_metadata(
        parameters={
            "Chat ID": CHAT_ID,
            "User ID": USER_ID,
            "Is Anonymous": IS_ANONYMOUS,
            "Can Edit The Info": CAN_EDIT_INFO,
            "Can Post Messages": CAN_POST_MESSAGES,
            "Can Edit Messages": CAN_EDIT_MESSAGES,
            "Can Delete Messages": CAN_DELETE_MESSAGES,
            "Can Invite Users": CAN_INVITE_USERS,
            "Can Restrict Members": CAN_RESTRICT_USERS,
            "Can Promote Members": CAN_PROMOTE_MEMBERS,
            "Can Pin Messages": CAN_PIN_MESSAGES,
        },
        integration_config_file_path=CONFIG_PATH,
    )
    def test_set_user_permissions_success(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
    ) -> None:
        SetUserPermissions()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/promoteChatMember")
        assert request.kwargs["data"] == {
            "chat_id": self.CHAT_ID,
            "user_id": self.USER_ID,
            "is_anonymous": self.IS_ANONYMOUS,
            "can_change_info": self.CAN_EDIT_INFO,
            "can_post_messages": self.CAN_POST_MESSAGES,
            "can_edit_messages": self.CAN_EDIT_MESSAGES,
            "can_delete_messages": self.CAN_DELETE_MESSAGES,
            "can_invite_users": self.CAN_INVITE_USERS,
            "can_restrict_users": self.CAN_RESTRICT_USERS,
            "can_pin_messages": self.CAN_PIN_MESSAGES,
            "can_promote_members": self.CAN_PROMOTE_MEMBERS,
        }

        assert action_output.results.output_message == f"The permissions of the user {self.USER_ID} were set successfully"
        assert action_output.results.execution_state == ExecutionState.COMPLETED
        assert action_output.results.json_output.json_result == {"ok": True, "result": {"chat_id": self.CHAT_ID, "user_id": self.USER_ID, "is_anonymous": self.IS_ANONYMOUS, "can_change_info": self.CAN_EDIT_INFO, "can_post_messages": self.CAN_POST_MESSAGES, "can_edit_messages": self.CAN_EDIT_MESSAGES, "can_delete_messages": self.CAN_DELETE_MESSAGES, "can_invite_users": self.CAN_INVITE_USERS, "can_restrict_users": self.CAN_RESTRICT_USERS, "can_pin_messages": self.CAN_PIN_MESSAGES, "can_promote_members": self.CAN_PROMOTE_MEMBERS}}

    @set_metadata(
        parameters={
            "Chat ID": CHAT_ID,
            "User ID": USER_ID,
            "Is Anonymous": IS_ANONYMOUS,
            "Can Edit The Info": CAN_EDIT_INFO,
            "Can Post Messages": CAN_POST_MESSAGES,
            "Can Edit Messages": CAN_EDIT_MESSAGES,
            "Can Delete Messages": CAN_DELETE_MESSAGES,
            "Can Invite Users": CAN_INVITE_USERS,
            "Can Restrict Members": CAN_RESTRICT_USERS,
            "Can Promote Members": CAN_PROMOTE_MEMBERS,
            "Can Pin Messages": CAN_PIN_MESSAGES,
        },
        integration_config_file_path=CONFIG_PATH,
    )
    def test_set_user_permissions_failure(
        self,
        script_session: TelegramSession,
        action_output: MockActionOutput,
        telegram: Telegram
    ) -> None:
        telegram.fail_next_call()
        SetUserPermissions()

        assert len(script_session.request_history) == 1
        request = script_session.request_history[0].request
        assert request.url.path.endswith("/promoteChatMember")
        assert request.kwargs["data"] == {
            "chat_id": self.CHAT_ID,
            "user_id": self.USER_ID,
            "is_anonymous": self.IS_ANONYMOUS,
            "can_change_info": self.CAN_EDIT_INFO,
            "can_post_messages": self.CAN_POST_MESSAGES,
            "can_edit_messages": self.CAN_EDIT_MESSAGES,
            "can_delete_messages": self.CAN_DELETE_MESSAGES,
            "can_invite_users": self.CAN_INVITE_USERS,
            "can_restrict_users": self.CAN_RESTRICT_USERS,
            "can_pin_messages": self.CAN_PIN_MESSAGES,
            "can_promote_members": self.CAN_PROMOTE_MEMBERS,
        }

        assert action_output.results.output_message == "Could not set user permissions. Error: b'Simulated API failure for SetUserPermissions'"
        assert action_output.results.execution_state == ExecutionState.FAILED
