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

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler
from TIPCommon.rest.soar_api import get_email_template


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.SCRIPT_NAME = "Get Email Templates"

    template_type = siemplify.extract_action_param("Template Type", print_value=True)

    status = EXECUTION_STATE_COMPLETED
    output_message = (
        "output message :"  # human readable message, showed in UI as the action result
    )

    email_templates = get_email_template(siemplify)
    HTML_TYPES = {1, "HtmlFormat"}
    STANDARD_TYPES = {0, "Template"}
    res = []

    for template in email_templates:
        template_json = template.to_json()
        template_type_value = template_json.get("type")

        if (
            (template_type == "HTML" and template_type_value in HTML_TYPES)
            or
            (template_type == "Standard" and template_type_value in STANDARD_TYPES)
        ):
            res.append(template_json)

    siemplify.result.add_result_json({"templates": res})
    siemplify.end(output_message, json.dumps(res), status)


if __name__ == "__main__":
    main()
