# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import copy
import json

import requests
from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import convert_dict_to_json_result_dict, output_handler

GET_ENTITY_URL = "{}/external/v1/entities/GetEntityData?format=camel"

HEADERS = {"Content-Type": "application/json", "Accept": "*/*"}
SCRIPT_NAME = "Enrich Entity from Explorer"
SYSTEM_FIELDS = [
    "Type",
    "Environment",
    "OriginalIdentifier",
    "IsInternalAsset",
    "IsSuspicious",
    "IsEnriched",
    "IsVulnerable",
    "IsArtifact",
    "IsTestCase",
    "Network_Priority",
    "NetworkPriority",
    "Alert_Id",
    "AlertID",
    "IsManuallyCreated",
    "IsFromLdapString",
    "IsAttacker",
]


def pascal_to_snake(s):
    if not s:
        return s

    snake_case = [s[0].lower()]
    for char in s[1:]:
        if char.isupper():
            snake_case.append("_")
            snake_case.append(char.lower())
        else:
            snake_case.append(char)

    return "".join(snake_case)


@output_handler
def main():
    status = EXECUTION_STATE_COMPLETED
    output_message = "output message : "
    json_results = {}
    # Set our headers var
    headers = copy.deepcopy(HEADERS)
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    try:
        # Get our bearer token
        entities_to_update = []
        conf = siemplify.get_configuration("Enrichment")
        api_key = conf.get("API Key")
        verify_ssl = (
            True if conf.get("Verify SSL", "False").casefold() == "true" else False
        )
        allowlist = (
            siemplify.extract_action_param(
                "Use Field Name as Whitelist",
                print_value=True,
                default_value="true",
            ).lower()
            == "true"
        )
        field_name = siemplify.parameters.get("Field Name")
        if field_name:
            entity_fields = list(
                filter(None, [x.strip() for x in field_name.split(",")]),
            )
        else:
            entity_fields = []

        headers["AppKey"] = api_key
        # Loop through all targeted entities
        for entity in siemplify.target_entities:
            json_payload = {
                "entityIdentifier": entity.identifier,
                "entityEnvironment": siemplify._environment,
                "entityType": entity.entity_type,
                "lastCaseType": 0,
                "caseDistributationType": 0,
            }
            res = requests.post(
                GET_ENTITY_URL.format(siemplify.API_ROOT),
                json=json_payload,
                headers=headers,
                verify=verify_ssl,
            )
            res.raise_for_status()
            entity_data = res.json()["entity"]
            entity_data_items = enumerate(entity_data["fields"][0]["items"])
            property_value = None
            updated_fields = {}

            for indice, field in entity_data_items:
                entity_field = None

                # Does the entity have the field we're looking for?
                if allowlist:  # if allowlist is enabled, check if entity has field
                    if entity_fields:
                        if field["originalName"] in entity_fields:
                            entity_field = field["originalName"]
                            property_value = field["value"]
                    else:
                        entity_field = field["originalName"]
                        property_value = field["value"]
                elif entity_fields:
                    if field["originalName"] in entity_fields:
                        continue
                else:
                    entity_field = field["originalName"]
                    property_value = field["value"]
                    # Does the existing entity already have the field? Update or add.
                if (
                    entity_field
                    and entity_field not in SYSTEM_FIELDS
                    and entity_field
                    not in [pascal_to_snake(field) for field in SYSTEM_FIELDS]
                ):  # Check to see if field is in SYSTEM_FIELDS, skip if it is.
                    if hasattr(entity, entity_field):
                        setattr(entity, entity_field, property_value)
                    else:
                        entity.additional_properties[entity_field] = property_value
                    updated_fields[entity_field] = property_value
            if updated_fields:
                output_message += f"The properties: {', '.join(list(updated_fields.keys()))} was changed for entity: {entity.identifier}.\n"
                entities_to_update.append(entity)

            # Prepare the json results for Siemplify
            json_results[entity.identifier] = updated_fields

        # Update the entities we need to update
        if entities_to_update:
            siemplify.LOGGER.info("Updating entities")
            siemplify.update_entities(entities_to_update)
            siemplify.result.add_result_json(
                convert_dict_to_json_result_dict(json_results),
            )
            siemplify.result.add_json(
                "EnrichEntityExplorer",
                convert_dict_to_json_result_dict(json_results),
            )

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)

    siemplify.end(output_message, json.dumps(json_results), status)


if __name__ == "__main__":
    main()
