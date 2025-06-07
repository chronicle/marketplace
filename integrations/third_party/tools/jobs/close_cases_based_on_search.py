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
from urllib.parse import urljoin

import requests
from soar_sdk.SiemplifyJob import SiemplifyJob
from soar_sdk.SiemplifyUtils import output_handler

SCRIPT_NAME = "CloseCasesBasedOnSearch"


def get_bearer_token(siemplify, username, password):
    address = urljoin(siemplify.API_ROOT, "api/external/v1/accounts/Login?format=camel")
    response = siemplify.session.post(
        address,
        json={"Username": username, "Password": password},
        verify=False,
    )
    response.raise_for_status()
    return response.json()["token"]


SEARCH_URL = "api/external/v1/search/CaseSearchEverything"
BULK_CLOSE_URL = "api/external/v1/cases-queue/bulk-operations/ExecuteBulkCloseCase"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME  # In order to use the SiemplifyLogger, you must assign a name to the script.
    username = siemplify.parameters["Siemplify Username"]
    password = siemplify.parameters["Siemplify Password"]
    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        bearer_token = get_bearer_token(siemplify, username, password)

        session = requests.Session()
        session.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {bearer_token}",
        }
        session.verify = False

        payload = json.loads(siemplify.parameters.get("Search Payload"))
        payload["isCaseClosed"] = False
        res_search = session.post(urljoin(siemplify.API_ROOT, SEARCH_URL), json=payload)
        res_search.raise_for_status()

        results = res_search.json().get("results")
        case_ids = [item.get("id") for item in results]

        if case_ids:
            siemplify.LOGGER.info(f"The following cases will be affected: {case_ids}")

            close_payload = {
                "casesIds": case_ids,
                "closeComment": siemplify.parameters.get("Close Comment"),
                "closeReason": int(siemplify.parameters.get("Close Reason")),
                "rootCause": siemplify.parameters.get("Root Cause"),
            }

            res_close = session.post(
                urljoin(siemplify.API_ROOT, BULK_CLOSE_URL),
                json=close_payload,
            )
            res_close.raise_for_status()
            siemplify.LOGGER.info(f"Successfully closed {len(case_ids)} cases")

        else:
            siemplify.LOGGER.info("No cases found with the search payload")

    except Exception as e:
        siemplify.LOGGER.error(f"General error performing Job {SCRIPT_NAME}")
        siemplify.LOGGER.exception(e)
        raise

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end_script()


if __name__ == "__main__":
    main()
