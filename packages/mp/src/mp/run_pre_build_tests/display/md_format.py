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


import pathlib

from mp.run_pre_build_tests.process_test_output import IntegrationTestResults, TestIssue


class MdFormat:
    """Formats a list of IntegrationTestResults into a Markdown report
    and saves it to a file using a hierarchical list format.
    """

    def __init__(self, test_results: list[IntegrationTestResults]):
        self.test_results: list[IntegrationTestResults] = test_results
        self._report_lines: list[str] = []

    def _format_summary_table(self, result: IntegrationTestResults) -> None:
        """Adds a markdown table with the summary of test results."""
        self._report_lines.append("| ✅ Passed | ❌ Failed | ⏭️ Skipped |")
        self._report_lines.append("|:---------:|:--------:|:----------:|")
        self._report_lines.append(
            f"| {result.passed_tests} | {result.failed_tests} | {result.skipped_tests} |"
        )
        self._report_lines.append("")  # Add a blank line for spacing

    def _format_issues(self, title: str, issues: list[TestIssue], emoji: str) -> None:
        """Formats a list of test issues (failed or skipped) into a collapsible section."""
        if not issues:
            return

        self._report_lines.append(f"### {emoji} {title}")
        for issue in issues:
            self._report_lines.append("<details>")
            self._report_lines.append(f"<summary>{issue.test_name}</summary>\n")
            self._report_lines.append("```")
            self._report_lines.append(issue.stack_trace)
            self._report_lines.append("```")
            self._report_lines.append("</details>")
        self._report_lines.append("")  # Add a blank line for spacing

    def display(self) -> None:
        """Generates and saves the test report to 'test_report.md'.
        If there are no test results, it prints a message to the console.
        """
        if not self.test_results:
            print("✅ All Test Passed")
            return

        self._report_lines.append("# 🧪 Integration Test Report")
        self._report_lines.append("")

        for result in self.test_results:
            # Integration name and summary are always visible.
            self._report_lines.append(f"<h2>🧩   {result.integration_name}</h2>")
            self._report_lines.append("")  # Ensure a blank line after HTML for markdown parsing.
            self._format_summary_table(result)

            # Issues are in collapsible sections.
            self._format_issues("Failed Tests", result.failed_tests_summary, "❌")
            self._format_issues("Skipped Tests", result.skipped_tests_summary, "⏭️")

            # Add spacing between integrations.
            self._report_lines.append("")
            self._report_lines.append("")
            self._report_lines.append("")

        report_content = "\n".join(self._report_lines)

        _save_report_file(report_content, "test_report.md")


def _save_report_file(markdown_content_str: str, output_filename: str) -> None:
    output_dir = pathlib.Path("./artifacts")
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / output_filename
    report_path.write_text(markdown_content_str, encoding="utf-8")
