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

import re

from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

from ..core.constants import COMMIT_AUTHOR_REGEX, DEFAULT_AUTHOR, DEFAULT_USERNAME
from ..core.GitSyncManager import GitSyncManager

SCRIPT_NAME = "Ping"
INTEGRATION_NAME = "GitSync"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME
    smp_credentials = {}
    repo_url = siemplify.extract_configuration_param(INTEGRATION_NAME, "Repo URL")
    branch = siemplify.extract_configuration_param(INTEGRATION_NAME, "Branch")
    git_password = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "Git Password/Token/SSH Key",
    )
    git_username = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "Git Username",
        default_value=DEFAULT_USERNAME,
    )
    git_author = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "Commit Author",
        default_value=DEFAULT_AUTHOR,
    )
    smp_credentials["username"] = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "SOAR Username",
        print_value=True,
        default_value=None,
    )
    smp_credentials["password"] = siemplify.extract_configuration_param(
        provider_name=INTEGRATION_NAME,
        param_name="SOAR Password",
    )
    smp_verify = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "Siemplify Verify SSL",
        input_type=bool,
    )
    git_verify = siemplify.extract_configuration_param(
        INTEGRATION_NAME,
        "Git Verify SSL",
        input_type=bool,
    )

    if not re.fullmatch(COMMIT_AUTHOR_REGEX, git_author):
        raise Exception(
            "Commit Author parameter must be in the following format: Name <example@gmail.com>",
        )

    try:
        gitsync = GitSyncManager(
            siemplify,
            repo_url,
            branch,
            git_password,
            git_username,
            git_author,
            smp_credentials,
            smp_verify,
            git_verify,
        )
    except Exception as e:
        raise Exception(f"Couldn't connect to git\nError: {e}")

    try:
        gitsync.api.test_connectivity()
    except Exception:
        raise Exception("Couldn't connect to Chronicle SOAR.")

    siemplify.end("True", True)


if __name__ == "__main__":
    main()
