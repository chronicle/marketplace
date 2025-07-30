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


import datetime
import os
import pathlib
import tempfile
import webbrowser

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

from mp.validate.validation_results import ValidationResults

console = Console()


class HtmlDisplay:
    validation_results: dict[str, list[ValidationResults] | None]

    def __init__(self, validation_results: dict[str, list[ValidationResults] | None]) -> None:
        self.validation_results = validation_results

    def display(self) -> None:
        """Generate an HTML report for validation results."""
        try:
            html_content = self._generate_validation_report_html()
            is_github_actions = os.getenv("GITHUB_ACTIONS") == "true"
            report_path: pathlib.Path

            if is_github_actions:
                output_dir = pathlib.Path("./artifacts")
                output_dir.mkdir(exist_ok=True)
                report_path = output_dir / "validation-report.html"
                report_path.write_text(html_content, encoding="utf-8")
            else:
                with tempfile.NamedTemporaryFile(
                    mode="w", delete=False, suffix=".html", encoding="utf-8"
                ) as temp_file:
                    temp_file.write(html_content)
                    report_path = pathlib.Path(temp_file.name)

            resolved_path = report_path.resolve()

            if not is_github_actions:
                console.print(f"📂 Report available at 👉: {resolved_path.as_uri()}")
                webbrowser.open(resolved_path.as_uri())
            else:
                server_url = os.getenv("GITHUB_SERVER_URL")
                repository = os.getenv("GITHUB_REPOSITORY")
                run_id = os.getenv("GITHUB_RUN_ID")

                if server_url and repository and run_id:
                    artifact_url = f"{server_url}/{repository}/actions/runs/{run_id}"
                    console.print("\n[bold cyan]View Report for full details:[/bold cyan]")
                    console.print(f"👉 {artifact_url}\n")
                else:
                    console.print(f"Artifact path for CI: {resolved_path}")

        except Exception as e:  # noqa: BLE001
            console.print(f"❌ Error generating report: {e}")

    def _generate_validation_report_html(self, template_name: str = "report.html") -> str:
        script_dir = pathlib.Path(__file__).parent.resolve()
        env = Environment(
            loader=FileSystemLoader(script_dir), autoescape=select_autoescape(["html"])
        )
        template = env.get_template(template_name)
        all_reports = [
            report
            for reports_list in self.validation_results.values()
            if reports_list is not None
            for report in reports_list
        ]

        system_local_timezone = datetime.datetime.now().astimezone().tzinfo
        current_time_aware = datetime.datetime.now(system_local_timezone)

        context = {
            "reports_by_category": self.validation_results,
            "total_integrations": len(all_reports),
            "total_fatal_issues": sum(
                len(r.validation_report.failed_fatal_validations) for r in all_reports
            ),
            "total_non_fatal_issues": sum(
                len(r.validation_report.failed_non_fatal_validations) for r in all_reports
            ),
            "current_time": current_time_aware.strftime("%B %d, %Y at %I:%M %p %Z"),
        }
        return template.render(context)
