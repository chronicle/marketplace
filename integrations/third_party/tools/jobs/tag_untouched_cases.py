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

import datetime

from soar_sdk.SiemplifyJob import SiemplifyJob
from soar_sdk.SiemplifyUtils import output_handler

SCRIPT_NAME = "TagCasesBasedOnLastModifiedTime"


@output_handler
def main():
    siemplify = SiemplifyJob()
    siemplify.script_name = SCRIPT_NAME  # In order to use the SiemplifyLogger, you must assign a name to the script.
    maxTime = siemplify.parameters.get("Unmodified Time")
    tags = siemplify.parameters.get("Tags")

    siemplify.LOGGER.info("----------------- Main - Started -----------------")
    try:
        timeNow = datetime.datetime.now()
        update_time_to = timeNow - datetime.timedelta(hours=int(maxTime))

        case_ids = siemplify.get_cases_ids_by_filter(
            status="OPEN",
            start_time_from_unix_time_in_ms=None,
            start_time_to_unix_time_in_ms=None,
            close_time_from_unix_time_in_ms=None,
            close_time_to_unix_time_in_ms=None,
            update_time_from_unix_time_in_ms=None,
            update_time_to_unix_time_in_ms=update_time_to.timestamp() * 1000,
            operator=None,
            sort_by="START_TIME",
            sort_order="DESC",
            max_results=10000,
        )

        if len(case_ids):
            siemplify.LOGGER.info(f"The following cases will be affected: {case_ids}")
            tags_list = []
            tags_list.extend(t.strip() for t in tags.split(","))
            tags_string = ", ".join(tags_list)

            for cid in case_ids:
                for tag in tags_list:
                    siemplify.add_tag(tag=tag, case_id=cid, alert_identifier=None)

            siemplify.LOGGER.info(
                f"Successfully Tagged {len(case_ids)} cases with tags: {tags_string}",
            )

        else:
            siemplify.LOGGER.info(
                f"No Cases open for longer than {maxTime} hours were found",
            )

    except Exception as e:
        siemplify.LOGGER.error(f"General error performing Job {SCRIPT_NAME}")
        siemplify.LOGGER.exception(e)
        raise

    siemplify.LOGGER.info("----------------- Main - Finished -----------------")
    siemplify.end_script()


if __name__ == "__main__":
    main()
