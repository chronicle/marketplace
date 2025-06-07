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

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_INPROGRESS
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

GET_ALERT_WFS = "{0}/external/v1/cases/GetWorkflowInstancesCards?format=camel"
WF_STATUS_INPROGRESS = 1
WF_STATUS_COMPLETED = 2
WF_STATUS_FAILED = 3
WF_STATUS_PENDING = 4
WF_STATUS_TERMINATED = 5


def get_wf_status(siemplify: SiemplifyAction, workflow_name: str) -> int:
    """Get workflow status for current alert.

    Args:
        siemplify (SiemplifyAction): SiemplifyAction object.
        workflow_name (str): Playbook name.

    Returns:
        int: playbook execution status.

    """
    payload = {
        "caseId": siemplify.case_id,
        "alertIdentifier": siemplify.current_alert.alert_group_identifier,
    }
    alert_wfs_res = siemplify.session.post(
        GET_ALERT_WFS.format(siemplify.API_ROOT),
        json=payload,
    )
    siemplify.validate_siemplify_error(alert_wfs_res)
    for alert_wf in alert_wfs_res.json():
        if alert_wf["name"] == workflow_name:
            return alert_wf["status"]

    return None


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = "Wait for Playbook to Complete"
    playbook_name = siemplify.parameters.get("Playbook Name", None)
    wf_status = get_wf_status(siemplify, playbook_name)

    if wf_status == WF_STATUS_COMPLETED:
        output_message = (
            f"Alert Id: {siemplify.current_alert.identifier}, "
            f"Playbook: {playbook_name} Finished. Lock Released. "
        )
        result_value = "true"
        status = EXECUTION_STATE_COMPLETED

    elif wf_status == WF_STATUS_FAILED:
        output_message = (
            f"Alert Id: {siemplify.current_alert.identifier}, "
            f"Playbook: {playbook_name} Failed. Lock Released. "
        )
        result_value = "true"
        status = EXECUTION_STATE_COMPLETED

    elif wf_status == WF_STATUS_TERMINATED:
        output_message = (
            f"Alert Id: {siemplify.current_alert.identifier}, "
            f"Playbook: {playbook_name} terminated. Lock Released. "
        )
        result_value = "true"
        status = EXECUTION_STATE_COMPLETED

    elif wf_status == WF_STATUS_INPROGRESS or wf_status == WF_STATUS_PENDING:
        output_message = (
            f"Alert Id: {siemplify.current_alert.identifier}: "
            f"Playbook {playbook_name} Inprogress. Current playbook locked."
        )
        result_value = "false"
        status = EXECUTION_STATE_INPROGRESS

    else:
        output_message = (
            f"Alert Id: {siemplify.current_alert.identifier}: "
            f"Playbook {playbook_name} not found."
        )
        result_value = "true"
        status = status = EXECUTION_STATE_COMPLETED

    siemplify.end(output_message, result_value, status)


if __name__ == "__main__":
    main()
