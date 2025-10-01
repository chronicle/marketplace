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

import json

import requests
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler


@output_handler
def main():
    siemplify = SiemplifyAction()

    description = siemplify.parameters.get("Description")
    name = siemplify.parameters.get("Name")
    file_type = siemplify.parameters.get("Type")
    base64_blob = siemplify.parameters.get("Base64 Blob")
    isFavorite = (
        True
        if siemplify.parameters.get("isFavorite", "False").casefold() == "true"
        else False
    )
    headers = {"AppKey": siemplify.api_key, "Content-Type": "application/json"}

    conf = siemplify.get_configuration("FileUtilities")
    verify_ssl = True if conf.get("Verify SSL", "False").casefold() == "true" else False
    case_id = int(siemplify.case.identifier)

    body = {
        "CaseIdentifier": case_id,
        "Base64Blob": base64_blob,
        "Name": name,
        "Description": description,
        "Type": file_type,
        "IsImportant": isFavorite,
    }
    response = requests.post(
        f"{siemplify.API_ROOT}/external/v1/cases/AddEvidence/",
        json=body,
        headers=headers,
        verify=verify_ssl,
    )
    json_response = response.json()

    siemplify.result.add_result_json(json.dumps(json_response))

    siemplify.end("Max number , Min Number", True)


if __name__ == "__main__":
    main()
