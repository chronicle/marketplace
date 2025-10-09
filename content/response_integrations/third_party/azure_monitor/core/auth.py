from __future__ import annotations

import dataclasses
from requests import Session
from TIPCommon.base.interfaces import Authable
from TIPCommon.base.utils import CreateSession
from TIPCommon.extraction import extract_script_param
from TIPCommon.types import ChronicleSOAR
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyConnectors import SiemplifyConnectorExecution
from soar_sdk.SiemplifyJob import SiemplifyJob

from .constants import (
    DEFAULT_API_ROOT,
    DEFAULT_LOGIN_API_ROOT,
    DEFAULT_VERIFY_SSL,
    INTEGRATION_IDENTIFIER,
)
from .data_models import IntegrationParameters


@dataclasses.dataclass(slots=True)
class SessionAuthenticationParameters:
    verify_ssl: bool


def build_auth_params(soar_sdk_object: ChronicleSOAR) -> IntegrationParameters:
    sdk_class = type(soar_sdk_object).__name__
    if sdk_class == SiemplifyAction.__name__:
        input_dictionary = soar_sdk_object.get_configuration(INTEGRATION_IDENTIFIER)
    elif sdk_class in (SiemplifyConnectorExecution.__name__, SiemplifyJob.__name__):
        input_dictionary = soar_sdk_object.parameters
    else:
        raise ValueError(f"Unsupported SOAR object type: {sdk_class}")

    login_api_root = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Login API Root",
        default_value=DEFAULT_LOGIN_API_ROOT,
        is_mandatory=True,
        print_value=True,
    )
    api_root = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="API Root",
        default_value=DEFAULT_API_ROOT,
        is_mandatory=True,
        print_value=True,
    )
    tenant_id = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Tenant ID",
        is_mandatory=True,
        print_value=True,
    )
    client_id = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Client ID",
        is_mandatory=True,
        print_value=True,
    )
    client_secret = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Client Secret",
        is_mandatory=True,
    )
    workspace_id = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Workspace ID",
        is_mandatory=True,
        print_value=True,
    )
    verify_ssl = extract_script_param(
        soar_sdk_object,
        input_dictionary=input_dictionary,
        param_name="Verify SSL",
        default_value=DEFAULT_VERIFY_SSL,
        input_type=bool,
        is_mandatory=True,
        print_value=True,
    )

    return IntegrationParameters(
        login_api_root=login_api_root,
        api_root=api_root,
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret,
        workspace_id=workspace_id,
        verify_ssl=verify_ssl,
    )


class AuthenticatedSession(Authable):
    def authenticate_session(self, params: SessionAuthenticationParameters) -> None:
        session: Session = CreateSession.create_session()
        session.verify = params.verify_ssl
        self.session = session
