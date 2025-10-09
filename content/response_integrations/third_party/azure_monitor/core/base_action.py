from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from TIPCommon.base.action import Action

from .auth import AuthenticatedSession, SessionAuthenticationParameters, build_auth_params
from .integration_client import AzureMonitorClient

if TYPE_CHECKING:
    import requests


class AzureAction(Action, ABC):
    def _init_api_clients(self) -> AzureMonitorClient:
        auth_params = build_auth_params(self.soar_action)
        authenticator: AuthenticatedSession = AuthenticatedSession()
        authenticator.authenticate_session(
            SessionAuthenticationParameters(
                verify_ssl=auth_params.verify_ssl,
            )
        )
        session: requests.Session = authenticator.session

        return AzureMonitorClient(
            authenticated_session=session,
            login_api_root=auth_params.login_api_root,
            api_root=auth_params.api_root,
            tenant_id=auth_params.tenant_id,
            client_id=auth_params.client_id,
            client_secret=auth_params.client_secret,
            verify_ssl=auth_params.verify_ssl,
            logger=self.logger,
        )
