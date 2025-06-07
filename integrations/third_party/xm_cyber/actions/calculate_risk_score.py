"""Calculate Risk Score and other fields for Alert filtration Action."""

from __future__ import annotations

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core.constants import (
    CHOKE_POINT_SCORE_FIELD_NAME,
    COMPROMISE_RISK_SCORE_FIELD_NAME,
    ENTITY_ID_FIELD,
    PREFIX_PARAMETER_FOR_LABELS,
)
from ..core.utils import convert_string, convert_to_numeric, string_to_list

RISK_MAPPING = {
    "NONE": 0,
    "INFORMATIVE": 1,
    "LOW": 2,
    "MEDIUM": 3,
    "HIGH": 4,
    "CRITICAL": 5,
}
REVERSE_RISK_MAPPING = {v: k for k, v in RISK_MAPPING.items()}


def calculate_score(event_type, event_properties, score_components):
    """Calculate a score based on a set of components.

    Args:
        event_properties (dict): A dictionary of event properties
        score_components (list): A list of tuples, where each tuple contains the following:
            1. The name of the field to check
            2. The score to add if the field matches
            3. The value to check in the field (optional)

    Returns:
        int: The calculated score

    """
    score = 1
    for component in score_components:
        field_name, score_value = component[:2]
        value_to_check = component[2] if len(component) == 3 else "TRUE"
        field_value = event_properties.get(
            PREFIX_PARAMETER_FOR_LABELS.format(event_type, field_name),
            "",
        )
        if field_value == value_to_check:
            score += score_value
    return score


def calculate_risk_score(event_type, event_properties):
    """Calculate risk score and other fields for Alert filtration Action based on event properties.

    Args:
        event_properties (dict): A dictionary of event properties

    Returns:
        dict: A dictionary containing the calculated risk score and other fields

    """
    base_risk_score = convert_to_numeric(
        event_properties.get("detection_outcomes_risk_score", "0"),
    )
    if base_risk_score == 0:
        base_risk_score = 45

        if event_properties.get("event_principal_namespace") == "kube-system":
            base_risk_score += 35

    impact_score_components = [
        ("Is Critical Asset", 0.2),
        ("Predefined Admin", 0.1),
        ("Highly Privileged", 0.1),
        (CHOKE_POINT_SCORE_FIELD_NAME, 0.1, "MEDIUM"),
        (CHOKE_POINT_SCORE_FIELD_NAME, 0.15, "HIGH"),
        (CHOKE_POINT_SCORE_FIELD_NAME, 0.2, "CRITICAL"),
        ("AD Risk to Domain", 0.1),
        ("AD Risky Principals", 0.1),
        ("AD Admins And DCs", 0.15),
    ]

    impact_score = calculate_score(
        event_type,
        event_properties,
        impact_score_components,
    )
    impact_score = min(impact_score, 1.7)

    probability_score_components = [
        ("User without MFA", 0.05),
        (COMPROMISE_RISK_SCORE_FIELD_NAME, 0.1, "MEDIUM"),
        (COMPROMISE_RISK_SCORE_FIELD_NAME, 0.15, "HIGH"),
        (COMPROMISE_RISK_SCORE_FIELD_NAME, 0.25, "CRITICAL"),
    ]

    probability_score = calculate_score(
        event_type,
        event_properties,
        probability_score_components,
    )

    calculated_risk_score = base_risk_score * probability_score * impact_score
    risk_score = min(calculated_risk_score, 100)

    labels_string = event_properties.get(
        PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Labels"),
        "",
    )
    labels = string_to_list(labels_string) if labels_string != "" else []

    return {
        "base_risk_score": base_risk_score,
        "risk_score": risk_score,
        "is_critical_asset": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Is Critical Asset"),
                "",
            ),
        ),
        "is_highly_privileged": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Highly Privileged"),
                "",
            ),
        ),
        "is_predefined_admin": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Predefined Admin"),
                "",
            ),
        ),
        "user_without_mfa": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "User without MFA"),
                "",
            ),
        ),
        "compromised_choke_point_score_level": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(
                    event_type,
                    CHOKE_POINT_SCORE_FIELD_NAME,
                ),
                "",
            ),
        ),
        "compromised_risk_score_level": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(
                    event_type,
                    COMPROMISE_RISK_SCORE_FIELD_NAME,
                ),
                "",
            ),
        ),
        "compromised_choke_point_score": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Choke Point Score"),
                "0",
            ),
        ),
        "compromised_risk_score": convert_string(
            event_properties.get(
                PREFIX_PARAMETER_FOR_LABELS.format(event_type, "Compromise Risk Score"),
                "0",
            ),
        ),
        "labels": labels,
    }


def generate_alert_json(event_json):
    """Generate an alert JSON object from a dictionary of event properties."""
    aggregated_values = {
        "base_risk_score": 0,
        "risk_score": 0,
        "is_critical_asset": False,
        "is_highly_privileged": False,
        "is_predefined_admin": False,
        "user_without_mfa": False,
        "compromised_risk_score_level": RISK_MAPPING["NONE"],
        "compromised_risk_score": 0,
        "compromised_choke_point_score_level": RISK_MAPPING["NONE"],
        "compromised_choke_point_score": 0,
        "labels": set(),
    }

    for event_properties in event_json.values():
        aggregated_values["base_risk_score"] = max(
            aggregated_values["base_risk_score"],
            int(event_properties.get("base_risk_score", 0)),
        )
        aggregated_values["risk_score"] = max(
            aggregated_values["risk_score"],
            int(event_properties.get("risk_score", 0)),
        )
        aggregated_values["compromised_choke_point_score"] = max(
            aggregated_values["compromised_choke_point_score"],
            int(event_properties.get("compromised_choke_point_score", 0)),
        )
        aggregated_values["compromised_risk_score"] = max(
            aggregated_values["compromised_risk_score"],
            int(event_properties.get("compromised_risk_score", 0)),
        )

        aggregated_values["is_critical_asset"] = aggregated_values[
            "is_critical_asset"
        ] or event_properties.get("is_critical_asset", False)
        aggregated_values["is_highly_privileged"] = aggregated_values[
            "is_highly_privileged"
        ] or event_properties.get("is_highly_privileged", False)
        aggregated_values["is_predefined_admin"] = aggregated_values[
            "is_predefined_admin"
        ] or event_properties.get("is_predefined_admin", False)
        aggregated_values["user_without_mfa"] = aggregated_values[
            "user_without_mfa"
        ] or event_properties.get("user_without_mfa", False)

        aggregated_values["compromised_risk_score_level"] = max(
            aggregated_values["compromised_risk_score_level"],
            RISK_MAPPING.get(
                event_properties.get("compromised_risk_score_level", "NONE"),
                RISK_MAPPING["NONE"],
            ),
        )
        aggregated_values["compromised_choke_point_score_level"] = max(
            aggregated_values["compromised_choke_point_score_level"],
            RISK_MAPPING.get(
                event_properties.get("compromised_choke_point_score_level", "NONE"),
                RISK_MAPPING["NONE"],
            ),
        )

        aggregated_values["labels"].update(event_properties.get("labels", []) or [])

    aggregated_values["labels"] = ",".join(
        str(label) for label in aggregated_values["labels"]
    )

    # Convert the scores back to the original Enum value
    aggregated_values["compromised_choke_point_score_level"] = REVERSE_RISK_MAPPING[
        aggregated_values["compromised_choke_point_score_level"]
    ]
    aggregated_values["compromised_risk_score_level"] = REVERSE_RISK_MAPPING[
        aggregated_values["compromised_risk_score_level"]
    ]
    return aggregated_values


@output_handler
def main():
    """Generate a JSON object mapping between entity ID and its details."""
    result_value = False
    entity_json = {}

    siemplify = SiemplifyAction()
    alert = siemplify.current_alert

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

                entity_json[entity_id] = calculate_risk_score(
                    entity_type,
                    event_properties,
                )

        if not entity_json:
            output_message = "No XM Cyber entity details found in the alert events."
        else:
            # Create JSON object final
            final_alert_json = generate_alert_json(entity_json)
            output_message = f"Successfully created Alert JSON object from the following entities: {list(entity_json.keys())}"
            siemplify.result.add_result_json(final_alert_json)

        status = EXECUTION_STATE_COMPLETED
        result_value = True
    except Exception as e:
        error_message = str(e)
        output_message = f"Failed to create Alert JSON object! Error: {error_message}"
        status = EXECUTION_STATE_FAILED

    siemplify.LOGGER.info(f"Status: {status}")
    siemplify.LOGGER.info(f"Result: {result_value}")
    siemplify.LOGGER.info(f"Output Message: {output_message}")

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
