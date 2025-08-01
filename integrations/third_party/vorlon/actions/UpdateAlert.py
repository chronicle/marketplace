from __future__ import annotations

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core.Constants import (
    INTEGRATION_DISPLAY_NAME,
    INTEGRATION_NAME,
    UPDATE_ALERT_SCRIPT_NAME,
)
from ..core.VorlonManager import VorlonManager


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = UPDATE_ALERT_SCRIPT_NAME
    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")

    api_root = siemplify.extract_configuration_param(
        provider_name=INTEGRATION_NAME,
        param_name="API Root",
    )
    client_id = siemplify.extract_configuration_param(
        provider_name=INTEGRATION_NAME,
        param_name="Client ID",
    )
    client_secret = siemplify.extract_configuration_param(
        provider_name=INTEGRATION_NAME,
        param_name="Client Secret",
    )

    alert_object = siemplify.extract_action_param(
        param_name="Alert Object",
        print_value=True,
    )

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        manager = VorlonManager(
            url=api_root,
            client_id=client_id,
            client_secret=client_secret,
        )
        updated_alert = manager.update_alert(alert_object=alert_object)
        siemplify.result.add_result_json(updated_alert)
        result = True
        status = EXECUTION_STATE_COMPLETED
        output_message = (
            f"Successfully updated the alert on the {INTEGRATION_DISPLAY_NAME} server"
        )

    except Exception as e:
        result = False
        status = EXECUTION_STATE_FAILED
        output_message = f"Failed to  updated the alert on the {INTEGRATION_DISPLAY_NAME} server! {e}"

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.LOGGER.info(f"Status: {status}")
    siemplify.LOGGER.info(f"Result: {result}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")

    siemplify.end(output_message, result, status)


if __name__ == "__main__":
    main()
