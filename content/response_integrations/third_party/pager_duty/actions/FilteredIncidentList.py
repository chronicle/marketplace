from __future__ import annotations

import json

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction

from ..core.constants import INTEGRATION_NAME, SCRIPT_NAME_FILTEREDLIST
from ..core.PagerDutyManager import PagerDutyManager


def parse_json_param(param_value):
    """
    Parses a parameter value that might be a JSON-formatted string list.
    """
    if isinstance(param_value, str) and param_value.strip().startswith("["):
        try:
            return json.loads(param_value)
        except json.JSONDecodeError:
            return None
    return param_value


def add_list_value_to_dict(param_list: list | None, params_dict: dict, param_key: str):
    """Adds a list of values directly to the parameters dictionary."""
    if param_list:
        cleaned_list = [item for item in param_list if item]
        if cleaned_list:
            params_dict[param_key] = cleaned_list
    return params_dict


def add_filter_to_dict(filter_name, filter_dict, filter_key):
    """Adds a single value to the dictionary if it exists."""
    if filter_name:
        filter_dict[filter_key] = filter_name
    return filter_dict


def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = INTEGRATION_NAME + SCRIPT_NAME_FILTEREDLIST
    configurations = siemplify.get_configuration(INTEGRATION_NAME)

    siemplify.LOGGER.info("----------------- Main - Param Init -----------------")
    api_token = configurations["api_key"]
    filter_params_dic = {}

    urgencies_list = parse_json_param(siemplify.extract_action_param("Urgencies"))
    service_ids_list = parse_json_param(siemplify.extract_action_param("Service_IDS"))
    team_ids_list = parse_json_param(siemplify.extract_action_param("Team_IDS"))
    user_ids_list = parse_json_param(siemplify.extract_action_param("User_IDS"))
    additional_data_list = parse_json_param(
        siemplify.extract_action_param("Additional_Data")
    )
    statuses_list = parse_json_param(
        siemplify.extract_action_param("Incidents_Statuses")
    )

    since = siemplify.extract_action_param("Since")
    until = siemplify.extract_action_param("Until")
    date_range = siemplify.extract_action_param("Data_Range")
    incident_key = siemplify.extract_action_param("Incident_Key")
    sort_by = siemplify.extract_action_param("Sort_By")

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    pager_duty = PagerDutyManager(api_token)

    try:
        siemplify.LOGGER.info("Started processing the parameters")

        filter_params_dic = add_list_value_to_dict(
            statuses_list, filter_params_dic, "statuses[]"
        )
        filter_params_dic = add_list_value_to_dict(
            service_ids_list, filter_params_dic, "service_ids[]"
        )
        filter_params_dic = add_list_value_to_dict(
            team_ids_list, filter_params_dic, "team_ids[]"
        )
        filter_params_dic = add_list_value_to_dict(
            user_ids_list, filter_params_dic, "user_ids[]"
        )
        filter_params_dic = add_list_value_to_dict(
            additional_data_list, filter_params_dic, "include[]"
        )
        filter_params_dic = add_list_value_to_dict(
            urgencies_list, filter_params_dic, "urgencies[]"
        )

        filter_params_dic = add_filter_to_dict(since, filter_params_dic, "since")
        filter_params_dic = add_filter_to_dict(until, filter_params_dic, "until")

        filter_params_dic = add_filter_to_dict(
            date_range, filter_params_dic, "date_range"
        )
        filter_params_dic = add_filter_to_dict(
            incident_key, filter_params_dic, "incident_key"
        )
        filter_params_dic = add_filter_to_dict(sort_by, filter_params_dic, "sort_by")

        siemplify.LOGGER.info("Finished processing all the parameters")

        incidents = pager_duty.list_filtered_incidents(filter_params_dic)
        siemplify.result.add_result_json(incidents)
        output_message = "Successfully retrieved Incidents\n"
        result_value = "true"
        status = EXECUTION_STATE_COMPLETED

    except Exception as e:
        output_message = (
            f"There was an error retrieving the filtered parameter list. {e!s}"
        )
        result_value = False
        status = EXECUTION_STATE_FAILED

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
