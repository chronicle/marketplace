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

import os
from typing import TYPE_CHECKING, Protocol

from .cli import CliDisplay
from .html.html import HtmlFormat
from .markdown_format import MarkdownFormat

if TYPE_CHECKING:
    from mp.run_pre_build_tests.process_test_output import IntegrationTestResults


class DisplayReport(Protocol):
    def display(self, test_results: list[IntegrationTestResults]) -> None:
        """Start point of the report creation and displaying."""


# TODO : FIND ANOTHER NAME FOR THE FUNCTION!!!!!!!!!
def display(test_results: list[IntegrationTestResults]) -> None:
    """Run the display logic and creates the required reports."""
    display_types_list: list[DisplayReport] = _build_display_objects(test_results)
    for report_type in display_types_list:
        report_type.display()


def _build_display_objects(test_results: list[IntegrationTestResults]) -> list[DisplayReport]:
    display_types_list: list[DisplayReport] = [CliDisplay(test_results)]

    is_github_actions = os.getenv("GITHUB_ACTIONS")
    if is_github_actions == "true":
        display_types_list.append(MarkdownFormat(test_results))
    else:
        display_types_list.append(HtmlFormat(test_results))

    return display_types_list
