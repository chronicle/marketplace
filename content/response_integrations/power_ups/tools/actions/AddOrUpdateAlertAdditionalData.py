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

from soar_sdk.SiemplifyAction import SiemplifyAction


def update_alert_additional_data(siemplify, additional_data):
    siemplify.update_alerts_additional_data(
        {siemplify.current_alert.identifier: json.dumps(additional_data)},
    )


def main():
    siemplify = SiemplifyAction()

    in_string = siemplify.parameters.get("Json Fields")
    if in_string:
        try:
            data = json.loads(in_string)
        except:
            data = in_string
    else:
        data = None

    additional_data = siemplify.current_alert.additional_data
    if additional_data:
        alert_data = json.loads(additional_data)
        if "list" not in alert_data:
            alert_data["list"] = []
        if "dict" not in alert_data:
            alert_data["dict"] = {}
        if "data" not in alert_data:
            alert_data["data"] = ""
    else:
        alert_data = {"dict": {}, "list": []}

    if data:
        try:
            if isinstance(data, list):
                alert_data["list"].extend(data)
            elif isinstance(data, dict):
                alert_data["dict"].update(data)
            else:
                alert_data["data"] = data
        except:
            raise

        update_alert_additional_data(siemplify, alert_data)

    output_message = "Alert data attached as JSON to the action result"
    siemplify.result.add_result_json(alert_data)
    result_value = len(alert_data)

    siemplify.end(output_message, result_value)


if __name__ == "__main__":
    main()
