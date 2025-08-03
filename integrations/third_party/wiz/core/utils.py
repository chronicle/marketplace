from __future__ import annotations

from typing import TYPE_CHECKING

from TIPCommon.extraction import extract_configuration_param

from core import constants
from core.datamodels import IntegrationParameters

if TYPE_CHECKING:
    from TIPCommon.types import ChronicleSOAR


def get_integration_parameters(chronicle_soar: ChronicleSOAR) -> IntegrationParameters:
    """Get the parameters object for Wiz's auth and api manager.

    Args:
        chronicle_soar (ChronicleSOAR): ChronicleSOAR object.

    Returns:
        IntegrationParameters: IntegrationParameters object.
    """
    api_root = extract_configuration_param(
        chronicle_soar,
        provider_name=constants.INTEGRATION_NAME,
        param_name="API Root",
        is_mandatory=True,
        print_value=True,
    )
    client_id = extract_configuration_param(
        chronicle_soar,
        provider_name=constants.INTEGRATION_NAME,
        param_name="Client ID",
        is_mandatory=True,
        print_value=True,
    )
    client_secret = extract_configuration_param(
        chronicle_soar,
        provider_name=constants.INTEGRATION_NAME,
        param_name="Client Secret",
        is_mandatory=True,
        remove_whitespaces=False,
    )
    verify_ssl: bool = extract_configuration_param(
        chronicle_soar,
        provider_name=constants.INTEGRATION_NAME,
        param_name="Verify SSL",
        is_mandatory=False,
        input_type=bool,
        print_value=True,
    )
    integration_params: IntegrationParameters = IntegrationParameters(
        api_root=api_root,
        client_id=client_id,
        client_secret=client_secret,
        verify_ssl=verify_ssl,
        siemplify_logger=chronicle_soar.LOGGER,
    )

    return integration_params
