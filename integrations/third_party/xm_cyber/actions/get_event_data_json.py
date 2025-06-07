"""Get Event Data JSON Action."""

from __future__ import annotations

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core.constants import (
    ENRICHED_PARAMETERS,
    ENTITY_ID_FIELD,
    PREFIX_PARAMETER_FOR_LABELS,
)
from ..core.utils import convert_string, get_integration_params


def get_entity_data(entity_type, event_data):
    """Create entity object from event.

    Args:
        entity_type (str): The type of field to look. Can be "user" or "asset".
        event_data (dict): Data of the event

    Returns:
        dict: The object containing mapping between entity ID and its properties

    """
    PARAMETERS = {*ENRICHED_PARAMETERS, "Entity Type"}
    data = {}
    for parameter in PARAMETERS:
        value = (
            event_data.get(
                PREFIX_PARAMETER_FOR_LABELS.format(entity_type, parameter),
                "",
            )
            or ""
        )
        converted_value = convert_string(value)
        if isinstance(converted_value, str) and converted_value == "":
            continue

        data[parameter] = converted_value

    return data


@output_handler
def main():
    """Generate a JSON object mapping between entity ID and its details."""
    result_value = False
    entity_json = {}

    siemplify = SiemplifyAction()
    alert = siemplify.current_alert
    _, base_url, _ = get_integration_params(siemplify)

    try:
        for event in alert.security_events:
            event_properties = event.additional_properties

            entity_id_map = {
                "asset": event_properties.get(ENTITY_ID_FIELD.format("asset")),
                "user": event_properties.get(ENTITY_ID_FIELD.format("user")),
            }

            for entity_type, entity_id in entity_id_map.items():
                if entity_id is None:
                    continue

                is_xm_cyber_entity = event_properties.get(
                    PREFIX_PARAMETER_FOR_LABELS.format(entity_type, "Entity Type"),
                )
                if not is_xm_cyber_entity:
                    continue

                entity_json[entity_id] = get_entity_data(entity_type, event_properties)

                # Add URL to the entity overview page in XM Cyber instance
                entity_json[entity_id]["url"] = (
                    f"{base_url}/#/report/entity/{entity_id}"
                )

            siemplify.result.add_result_json(entity_json)
            status = EXECUTION_STATE_COMPLETED
            result_value = True
            if not entity_json:
                output_message = "No XM Cyber entity details found in the alert events."
            else:
                output_message = f"Successfully created entity data object for the following entities: {list(entity_json.keys())}"

    except Exception as e:
        error_message = str(e)
        output_message = f"Failed to create JSON object for the entities found in events! Error: {error_message}"
        status = EXECUTION_STATE_FAILED

    siemplify.LOGGER.info(f"Status: {status}")
    siemplify.LOGGER.info(f"Result: {result_value}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
