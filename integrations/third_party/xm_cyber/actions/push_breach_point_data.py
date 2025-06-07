"""Push Breach Point Data Action."""

from __future__ import annotations

from typing import TYPE_CHECKING

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core.api_manager import ApiManager
from ..core.constants import (
    ATTRIBUTE_NAME,
    DATE_PARAMETERS,
    ENTITY_ID_FIELD,
    ERRORS,
    INTEGRATION_NAME,
    POSSIBLE_OPERATORS,
    PREFIX_PARAMETER_FOR_LABELS,
    STRINGIFIED_LIST_PARAMETERS,
)
from ..core.utils import (
    convert_string,
    get_integration_params,
    parse_the_date,
    string_to_list,
    validate_push_breach_point_inputs,
)
from ..core.xm_cyber_exception import XMCyberException

if TYPE_CHECKING:
    from datetime import datetime


def check_entity_matches_criteria(
    event,
    entity_type: str,
    entity_id: str,
    parameter: str,
    operator: str,
    input_value: str | float | datetime,
) -> tuple[bool, str]:
    """Check if the given entity matches the criteria of the input parameter and value.

    Args:
        event (SiemplifyEvent): The event object.
        entity_id (str): The ID of the entity.
        entity_type (str): The type of the entity (either "asset" or "user").
        parameter (str): The parameter of the entity to check.
        operator (str): The operator of the criteria.
        input_value (str): The value of the criteria.

    Returns:
        tuple: A tuple containing a boolean indicating if the entity matches the criteria, and a string with an error
        message if it doesn't.

    """
    event_properties = event.additional_properties

    # If parameter is All, then we can ignore the criteria, and push data for all entities
    if parameter == "All":
        return (True, "")

    # Fetch the value of entity.parameter
    entity_value = event_properties.get(
        PREFIX_PARAMETER_FOR_LABELS.format(entity_type, parameter),
    )
    if parameter == "entityID":
        entity_value = entity_id

    if entity_value is None:
        return (
            False,
            ERRORS["PUSH_BREACH_POINT"]["MISSING_PARAMETER"].format(
                event.identifier,
                PREFIX_PARAMETER_FOR_LABELS.format(entity_type, parameter),
            ),
        )

    # Convert the value to the expected type
    actual_value = (
        string_to_list(entity_value)
        if parameter in STRINGIFIED_LIST_PARAMETERS
        else convert_string(entity_value)
    )
    # Convert the value to the datetime type for date parameters
    if parameter in DATE_PARAMETERS:
        actual_value = parse_the_date(entity_value)

    # Run the criteria
    result = getattr(actual_value, POSSIBLE_OPERATORS[operator])(input_value)
    if result is NotImplemented:
        return (
            False,
            ERRORS["PUSH_BREACH_POINT"]["TYPE_MISMATCH"].format(
                event.identifier,
                actual_value,
                input_value,
            ),
        )

    # Invert the result in case we encounter "Not Contains" operator
    result ^= operator == "Not Contains"

    if result is False:
        return (
            False,
            ERRORS["PUSH_BREACH_POINT"]["CRITERIA_MISMATCH"].format(
                event.identifier,
                actual_value,
            ),
        )

    return (result, "")


def get_entities_to_push(
    alert,
    parameter: str,
    operator: str,
    input_value: str,
) -> tuple[list[str], str]:
    """Get entities to push attributes to based on the criteria.

    Args:
        alert (SiemplifyAlert): The alert object.
        parameter (str): The parameter of the entity to check.
        operator (str): The operator of the criteria.
        input_value (str): The value of the criteria.

    Returns:
        tuple: A tuple containing a list of entity IDs to push attributes to, and a string with an error message if an
        entity doesn't match the criteria.

    """
    entities_to_push: list[str] = []
    error_message: str = ""

    for event in alert.security_events:
        event_properties = event.additional_properties
        entity_id_map = {
            "asset": event_properties.get(ENTITY_ID_FIELD.format("asset")),
            "user": event_properties.get(ENTITY_ID_FIELD.format("user")),
        }

        if entity_id_map["asset"] is None and entity_id_map["user"] is None:
            error_message += ERRORS["PUSH_BREACH_POINT"]["MISSING_ENTITY_ID"].format(
                event.identifier,
                ENTITY_ID_FIELD.format("asset"),
                ENTITY_ID_FIELD.format("user"),
            )
            continue

        for entity_type, entity_id in entity_id_map.items():
            if entity_id is None:
                continue

            status, message = check_entity_matches_criteria(
                event,
                entity_type,
                entity_id,
                parameter,
                operator,
                input_value,
            )
            if status is False:
                error_message += message
            elif entity_id not in entities_to_push:
                entities_to_push.append(entity_id)

    return entities_to_push, error_message


def fetch_action_parameters(siemplify):
    """Fetch action parameters from Siemplify.

    Args:
        siemplify (SiemplifyAction): The SiemplifyAction instance.

    Returns:
        tuple: A tuple containing the parameter name, operator, value, and attribute name.

    """
    parameter = siemplify.extract_action_param("Parameter", is_mandatory=True)
    operator = siemplify.extract_action_param("Operator", is_mandatory=True)
    value = siemplify.extract_action_param(
        "Value",
        is_mandatory=True,
        input_type=str,
    ).strip()
    attribute_name = siemplify.extract_action_param(
        "Attribute Name",
        is_mandatory=True,
        default_value=ATTRIBUTE_NAME,
        input_type=str,
    ).strip()

    return parameter, operator, value, attribute_name


@output_handler
def main():
    """Push attribute for entities in XM Cyber that matches the configured criteria."""
    siemplify = SiemplifyAction()

    auth_type, base_url, api_key = get_integration_params(siemplify)

    result_value = False
    output = ""

    try:
        # Authenticate the configurations
        api_manager = ApiManager(auth_type, base_url, api_key, siemplify.LOGGER)
        if api_manager.error:
            raise XMCyberException(api_manager.error)

        # Fetch the action parameters
        parameter, operator, value, attribute_name = fetch_action_parameters(siemplify)

        # Validate the parameters
        is_valid, input_value = validate_push_breach_point_inputs(
            parameter,
            operator,
            value,
        )

        if not is_valid:
            raise XMCyberException(input_value)

        entities_to_push, output = get_entities_to_push(
            siemplify.current_alert,
            parameter,
            operator,
            input_value,
        )
        if entities_to_push:
            if not attribute_name:
                attribute_name = ATTRIBUTE_NAME
                print(
                    f"Attribute name is found blank. Hence, using default value: {ATTRIBUTE_NAME}",
                )

            if not api_manager.push_breach_point_data(entities_to_push, attribute_name):
                raise XMCyberException(api_manager.error)

        result_value = True

        output_message = output
        if not entities_to_push:
            output_message += (
                "No valid entities found to push that matches the criteria.\n"
            )
        else:
            output_message += (
                "\nSuccessfully pushed the attributes for the following entities:\n"
                + "\n".join(entities_to_push)
            )
        status = EXECUTION_STATE_COMPLETED
    except Exception as e:
        error_message = str(e)
        output_message = f"Failed to push attributes to the {INTEGRATION_NAME} server! Error: {error_message}"
        status = EXECUTION_STATE_FAILED

    siemplify.LOGGER.info(f"Status: {status}")
    siemplify.LOGGER.info(f"Result: {result_value}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
