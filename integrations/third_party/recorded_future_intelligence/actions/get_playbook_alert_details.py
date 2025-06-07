############################## TERMS OF USE ###################################
# The following code is provided for demonstration purposes only, and should  #
# not be used without independent verification. Recorded Future makes no      #
# representations or warranties, express, implied, statutory, or otherwise,   #
# regarding this code, and provides it strictly "as-is".                      #
# Recorded Future shall not be liable for, and you assume all risk of         #
# using the foregoing.                                                        #
###############################################################################

# ============================================================================#
# title           :Get Alert Details.py
# description     :This Module contains the Get Playbook Alert Details action
# author          :support@recordedfuture.com                       noqa: ERA001
# date            :09-03-2024
# python_version  :3.11                                             noqa: ERA001
# product_version :1.3
# ============================================================================#

from __future__ import annotations

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler
from TIPCommon.extraction import extract_action_param, extract_configuration_param

from ..core.constants import GET_PBA_DETAILS_SCRIPT_NAME, PROVIDER_NAME
from ..core.exceptions import (
    RecordedFutureNotFoundError,
    RecordedFutureUnauthorizedError,
)
from ..core.recorded_future_manager import RecordedFutureManager


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = GET_PBA_DETAILS_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_url = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="ApiUrl",
    )
    api_key = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="ApiKey",
    )
    verify_ssl = extract_configuration_param(
        siemplify,
        provider_name=PROVIDER_NAME,
        param_name="Verify SSL",
        default_value=False,
        input_type=bool,
    )

    alert_id = extract_action_param(
        siemplify,
        param_name="Playbook Alert ID",
        is_mandatory=True,
    )
    category = extract_action_param(siemplify, param_name="Category", is_mandatory=True)

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    is_success = False
    status = EXECUTION_STATE_FAILED

    try:
        recorded_future_manager = RecordedFutureManager(
            api_url,
            api_key,
            verify_ssl=verify_ssl,
            siemplify=siemplify,
        )
        alert_object = recorded_future_manager.get_pba_details(alert_id, category)
        siemplify.result.add_result_json(alert_object.to_json())
        siemplify.result.add_link("Web Report Link:", alert_object.alert_url)

        is_success = True
        status = EXECUTION_STATE_COMPLETED
        output_message = f"Successfully fetched the following Alert ID details from Recorded Future: \n{alert_id}"

    except RecordedFutureUnauthorizedError as e:
        output_message = (
            f"Unauthorized - please check your API token and try again. {e}"
        )
    except RecordedFutureNotFoundError as e:
        output_message = (
            "Requested Alert ID wasn't found in Recorded Future, "
            "or something went wrong in executing "
            f"action {GET_PBA_DETAILS_SCRIPT_NAME}. Reason: {e}"
        )
    except Exception as e:
        output_message = (
            f"Error executing action {GET_PBA_DETAILS_SCRIPT_NAME}. Reason: {e}"
        )

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(f"Output Message: {output_message}")
    siemplify.LOGGER.info(f"Result: {is_success}")
    siemplify.LOGGER.info(f"Status: {status}")

    siemplify.end(output_message, is_success, status)


if __name__ == "__main__":
    main()
