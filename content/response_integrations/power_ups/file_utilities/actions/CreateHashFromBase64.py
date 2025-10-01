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

import base64
import hashlib

from soar_sdk.ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from soar_sdk.SiemplifyAction import SiemplifyAction
from soar_sdk.SiemplifyUtils import output_handler

SCRIPT_NAME = "Create Hash From Base64"


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = SCRIPT_NAME

    action_status = EXECUTION_STATE_COMPLETED
    action_result = True
    output_message = "Successfully created hash from base64."
    res = []
    strings = siemplify.parameters["Base64"].split(
        siemplify.parameters["Base64 Separator"],
    )
    hash_algorythm = siemplify.parameters["Hash Algorythm"]
    names = siemplify.parameters.get("Names")
    try:
        if names:
            names = names.split(siemplify.parameters["Names Separator"])

            for s, n in zip(strings, names, strict=False):
                d = {
                    "Hash": getattr(hashlib, hash_algorythm)(
                        base64.b64decode(s),
                    ).hexdigest(),
                    "HashAlgorythm": hash_algorythm,
                }
                if siemplify.parameters["Include Base64"].lower() == "true":
                    d["Base64"] = s
                d["Name"] = n
                res.append(d)
        else:
            for s in strings:
                d = {
                    "Hash": getattr(hashlib, hash_algorythm)(
                        base64.b64decode(s),
                    ).hexdigest(),
                    "HashAlgorythm": hash_algorythm,
                }
                if siemplify.parameters["Include Base64"].lower() == "true":
                    d["Base64"] = s
                res.append(d)
        siemplify.result.add_json("Hashes", res)
        siemplify.result.add_result_json(res)
    except Exception as e:
        action_status = EXECUTION_STATE_FAILED
        output_message = f"Error: {e}"
        action_result = False

    siemplify.end(output_message, action_result, action_status)


if __name__ == "__main__":
    main()
