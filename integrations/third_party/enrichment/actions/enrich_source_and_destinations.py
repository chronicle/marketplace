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

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

INVESTIGATOR_URL = "{}/external/v1/investigator/GetInvestigatorData/{}?format=camel"

ACTION_NAME = "Enrich Source and Destinations"


def get_alert_entities(siemplify):
    return [
        entity
        for alert in siemplify.case.alerts
        for entity in alert.entities
        if alert.identifier == siemplify.current_alert.identifier
    ]


def get_ip_entities(siemplify):
    return [
        entity.identifier
        for entity in get_alert_entities(siemplify)
        if entity.entity_type == "ADDRESS"
    ]


def get_host_entities(siemplify):
    return [
        entity.identifier
        for entity in get_alert_entities(siemplify)
        if entity.entity_type == "HOSTNAME"
    ]


def get_current_alert(alerts, current_alert):
    for alert in alerts:
        if alert["identifier"] == current_alert:
            return alert


def get_sources_and_dest(alert):
    sources = []
    destinations = []
    for event_card in alert["securityEventCards"]:
        sources.extend(event_card["sources"])
        destinations.extend(event_card["destinations"])

    if sources and isinstance(sources[0], dict):
        sources = [x["identifier"] for x in sources]
    if destinations and isinstance(destinations[0], dict):
        destinations = [x["identifier"] for x in destinations]
    return (sources, destinations)


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME

    investigator_res = siemplify.session.get(
        INVESTIGATOR_URL.format(siemplify.API_ROOT, siemplify.case_id),
    )
    investigator_res.raise_for_status()
    alert = get_current_alert(
        investigator_res.json()["alerts"],
        siemplify.current_alert.identifier,
    )
    (sources, dests) = get_sources_and_dest(alert)
    updated_entities = []

    for source in sources:
        for entity in get_alert_entities(siemplify):
            if entity.identifier == source:
                entity.additional_properties.update({"isSource": "true"})
                updated_entities.append(entity)
                break
    for dest in dests:
        for entity in get_alert_entities(siemplify):
            if entity.identifier == dest:
                entity.additional_properties.update({"isDest": "true"})
                updated_entities.append(entity)
                break

    siemplify.update_entities(updated_entities)
    status = EXECUTION_STATE_COMPLETED  # used to flag back to siemplify system, the action final status
    output_message = "output message : Enrichment added."  # human readable message, showed in UI as the action result
    result_value = (
        None  # Set a simple result value, used for playbook if\else and placeholders.
    )

    siemplify.LOGGER.info(
        f"\n  status: {status}\n  result_value: {result_value}\n  output_message: {output_message}",
    )
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
