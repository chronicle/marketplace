from __future__ import annotations

from soar_sdk.SiemplifyAction import SiemplifyAction

from ..core.constants import INTEGRATION_NAME, SCRIPT_NAME_INCIDENTID
from ..core.Exceptions import PagerDutyException
from ..core.PagerDutyManager import PagerDutyManager


def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = INTEGRATION_NAME + SCRIPT_NAME_INCIDENTID
    configurations = siemplify.get_configuration(INTEGRATION_NAME)

    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")
    api_token = configurations["api_key"]
    incident_key = siemplify.extract_action_param("Incident Key").strip()
    email_from = siemplify.extract_action_param("Email").strip()

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    pager_duty = PagerDutyManager(api_token)

    try:
        siemplify.LOGGER.info(
            "Starting on getting the specific Incident with the Id given",
        )

        incident = pager_duty.get_incident_ID(incident_key, email_from)
        siemplify.LOGGER.info(incident)
        siemplify.result.add_result_json(incident)
        output_message = "Successfully retrieved Incident\n"
        result_value = True

    except PagerDutyException as e:
        output_message = f"No Incident Found {e!s}\n"
        result_value = False

    except Exception as e:
        output_message = f"There was a problem retrieveing the incident.{e!s}"
        result_value = False

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
