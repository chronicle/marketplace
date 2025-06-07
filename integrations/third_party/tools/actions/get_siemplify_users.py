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

GET_USERS_URL = "{}/external/v1/settings/GetUserProfiles"
ACTION_NAME = "GetSiemplifyUsers"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = ACTION_NAME

    hide_disabled = siemplify.parameters.get("Hide Disabled Users").lower() == "true"
    json_payload = {
        "searchTerm": "",
        "filterRole": False,
        "requestedPage": 0,
        "pageSize": 1000,
        "shouldHideDisabledUsers": hide_disabled,
    }

    siemplify_users = siemplify.session.post(
        GET_USERS_URL.format(siemplify.API_ROOT),
        json=json_payload,
    )
    siemplify_users.raise_for_status()
    siemplify.result.add_result_json(
        {"siemplifyUsers": siemplify_users.json()["objectsList"]},
    )
    output_message = "Returned Siemplify Users."
    siemplify.end(output_message, True)


if __name__ == "__main__":
    main()
