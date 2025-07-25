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

from enum import Enum


class ValidationTypes(Enum):
    """Enum representing the various stages of a build process."""

    PRE_BUILD = "pre_build"
    BUILD = "build"
    POST_BUILD = "post_build"


class ValidationResults:
    def __init__(self, integration_name: str, validation_type: ValidationTypes) -> None:
        self.integration_name: str = integration_name
        self.validation_type: ValidationTypes = validation_type
        self.errors: list[str] = []
        self.is_success: bool = True
