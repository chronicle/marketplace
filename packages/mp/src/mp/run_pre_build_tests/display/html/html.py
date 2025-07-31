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
import pathlib
import tempfile
import webbrowser

from jinja2 import Environment, FileSystemLoader, select_autoescape
from rich.console import Console

from mp.run_pre_build_tests.process_test_output import IntegrationTestResults

console = Console()


class HtmlDisplay:
    def __init__(self, integration_results_list: list[IntegrationTestResults]) -> None:
        self.integration_results_list: list[IntegrationTestResults] = integration_results_list

    def display(self) -> None:
        """Generate an HTML report for integration test results."""
        try:
            html_content = self._generate_validation_report_html()
            report_path: pathlib.Path

            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".html", encoding="utf-8"
            ) as temp_file:
                temp_file.write(html_content)
                report_path = pathlib.Path(temp_file.name)

            resolved_path = report_path.resolve()
            console.print(f"📂 Report available at 👉: {resolved_path.as_uri()}")
            webbrowser.open(resolved_path.as_uri())

        except Exception as e:  # noqa: BLE001
            console.print(f"❌ Error generating report: {e}")

    def _generate_validation_report_html(
        self, template_name: str = "html_report/report.html"
    ) -> str:
        script_dir = pathlib.Path(__file__).parent.resolve()
        template_dir = script_dir / "templates"
        env = Environment(
            loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html"])
        )
        template = env.get_template(template_name)

        css_file_path = template_dir / "static" / "style.css"
        js_file_path = template_dir / "static" / "script.js"

        css_content = css_file_path.read_text(encoding="utf-8-sig")
        js_content = js_file_path.read_text(encoding="utf-8-sig")

        all_results = self.integration_results_list

        total_integrations = len(all_results)
        total_failed_tests = sum(r.failed_tests for r in all_results)
        total_skipped_tests = sum(r.skipped_tests for r in all_results)

        system_local_timezone = datetime.datetime.now().astimezone().tzinfo
        current_time_aware = datetime.datetime.now(system_local_timezone)

        context = {
            "integration_results_list": all_results,
            "total_integrations": total_integrations,
            "total_skipped_tests": total_skipped_tests,
            "total_failed_tests": total_failed_tests,
            "current_time": current_time_aware.strftime("%B %d, %Y at %I:%M %p %Z"),
            "css_content": css_content,
            "js_content": js_content,
        }
        return template.render(context)
