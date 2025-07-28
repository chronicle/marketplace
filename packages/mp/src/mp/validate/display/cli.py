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

from mp.validate.validation_results import ValidationResults

console = Console()


class CliDisplay:
    validation_results: dict[str, list[ValidationResults] | None]

    def __init__(self, validation_results: dict[str, list[ValidationResults] | None]) -> None:
        self.validation_results: dict[str, list[ValidationResults] | None] = validation_results

    def display(self) -> None:
        """Display the validation result in the cli."""
        if self.is_results_empty():
            console.print("[bold green]All validations passed\n[/bold green]")

        display_categories = ["Pre-Build", "Build", "Post-Build"]

        for category in display_categories:
            category_validation_result: list[ValidationResults] = self.validation_results.get(
                category
            )
            if not category_validation_result:
                continue
            console.print(f"[bold underline green]{category} Validations\n[/bold underline green]")
            for integration_result in category_validation_result:
                console.print(
                    "[bold red]🛑 Few issues were detected in "
                    f"---- {integration_result.integration_name} ----\n[/bold red]"
                )
                for (
                    validation_result
                ) in integration_result.validation_report.failed_non_fatal_validations:
                    console.print(
                        f"[bold magenta]▶️ {validation_result.validation_name}[/bold magenta]"
                    )
                    console.print(
                        f"[bold yellow]⚠️ WARNING: {validation_result.info}\n[/bold yellow]"
                    )

    def is_results_empty(self) -> bool:
        for category in self.validation_results:
            if self.validation_results[category]:
                return False
        return True
