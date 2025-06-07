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

import nltk
from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import convert_dict_to_json_result_dict, output_handler

ENV_DOMAIN_URL = "{}/external/v1/settings/GetDomainAliases?format=camel"
THRESHOLD = 2


def get_page_results(siemplify, url):
    payload = {"searchTerm": "", "requestedPage": 0, "pageSize": 100}
    res = siemplify.session.post(url.format(siemplify.API_ROOT), json=payload)
    res.raise_for_status()
    results = res.json()["objectsList"]
    if res.json()["metadata"]["totalNumberOfPages"] > 1:
        for page in range(res.json()["metadata"]["totalNumberOfPages"] - 1):
            payload["requestedPage"] = page + 1
            res = siemplify.session.post(url.format(siemplify.API_ROOT), json=payload)
            res.raise_for_status()
            results.extend(res.json()["objectsList"])
    return results


def get_domains(siemplify):
    res = get_page_results(siemplify, ENV_DOMAIN_URL)
    env_domains = []
    for domain in res:
        if siemplify._environment in domain["environments"]:
            env_domains.append(domain)
    return env_domains


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "Look-A-Like Domains"
    status = EXECUTION_STATE_COMPLETED
    output_message = "output message :"
    result_value = "false"
    domains = get_domains(siemplify)
    updated_entities = []
    json_result = {}
    for entity in siemplify.target_entities:
        if entity.entity_type == "DOMAIN":
            json_result[entity.identifier] = {}
            look_a_like_domains = []
            for domain in domains:
                distance = nltk.edit_distance(
                    entity.identifier.lower(),
                    domain["domain"].lower(),
                )
                if distance >= 1 and distance < 4:
                    look_a_like_domains.append(domain["domain"])
                    output_message += f"Domain {entity.identifier} is a look alike to {domain['domain']} with a score of {distance}.  \n"
                    entity.is_suspicious = True
                    entity.additional_properties["look_a_like_domain"] = domain[
                        "domain"
                    ]
                    updated_entities.append(entity)
                    result_value = "true"
                json_result[entity.identifier]["look_a_like_domains"] = (
                    look_a_like_domains
                )

    count_updated_entities = len(updated_entities)

    if count_updated_entities > 0:
        siemplify.update_entities(updated_entities)

    for updated_entity in updated_entities:
        siemplify.result.add_result_json(convert_dict_to_json_result_dict(json_result))
    siemplify.LOGGER.info(
        f"\n  status: {status}\n  result_value: {result_value}\n  output_message: {output_message}",
    )
    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
