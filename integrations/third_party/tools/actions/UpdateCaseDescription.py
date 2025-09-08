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
from TIPCommon.rest.soar_api import change_case_description

ACTION_NAME = "UpdateCaseDescription"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME
    description = siemplify.parameters["Case Description"]
    case_id = siemplify.case_id

    change_case_description(
        chronicle_soar=siemplify,
        case_id=case_id,
        description=description,
    )

    output_message = f"The case description has been updated to: {description}"
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()
