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

import os

from mp.run_pre_build_tests.process_test_output import IntegrationTestResults

from .cli import CliDisplay
from .html.html import HtmlDisplay as HtmlDisplay
from .md_format import MdFormat


class Report:
    @classmethod
    def display(cls, test_results: list[IntegrationTestResults]) -> None:
        """Run the display logic and creates the required reports."""
        is_github_actions = os.getenv("GITHUB_ACTIONS")

        CliDisplay(test_results).display()

        if is_github_actions == "true":
            MdFormat(test_results).display()
        else:
            HtmlDisplay(test_results).display()
