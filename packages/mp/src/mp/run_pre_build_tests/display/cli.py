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

from rich.console import Console

from mp.run_pre_build_tests.process_test_output import IntegrationTestResults

console = Console()


class CliDisplay:
    def __init__(self, tests_report: list[IntegrationTestResults]) -> None:
        self.tests_report: list[IntegrationTestResults] = tests_report

    def display(self) -> None:
        """Display the tests result in the cli."""
        if not self.tests_report:
            console.print("[bold green]All Tests Passed\n[/bold green]")

        for integration_report in self.tests_report:
            console.print(
                "[bold red]\n🛑 Few tests failed in "
                f"---- {integration_report.integration_name} integration ----[/bold red]"
            )

            if integration_report.failed_tests > 0:
                console.print(f"Total Failed Tests: {integration_report.failed_tests}")
                for test_issue in integration_report.failed_tests_summary:
                    console.print(f"[bold yellow]⚠️  {test_issue.test_name}[/bold yellow]")
                console.print()
            if integration_report.skipped_tests > 0:
                console.print(f"Total Skipped Tests: {integration_report.skipped_tests}")
                for test_issue in integration_report.skipped_tests_summary:
                    console.print(f"[bold yellow]⚠️  {test_issue.test_name}[/bold yellow]")
                console.print()
