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

from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

TASK_URL = "{}/external/v1/cases/AssignUserToCase"
ACTION_NAME = "AssignCaseToUser"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME

    case_id = siemplify.parameters["Case Id"]
    assign_to = siemplify.parameters["Assign To"]
    alert_id = siemplify.parameters["Alert Id"]

    json_payload = {"caseId": case_id, "alertIdentifier": alert_id, "userId": assign_to}
    add_task = siemplify.session.post(
        TASK_URL.format(siemplify.API_ROOT),
        json=json_payload,
    )
    add_task.raise_for_status()
    output_message = add_task.json()
    siemplify.LOGGER.info(output_message)

    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()
