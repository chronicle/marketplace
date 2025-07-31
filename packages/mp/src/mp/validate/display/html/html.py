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

from mp.validate.validation_results import ValidationResults

console = Console()


class HtmlDisplay:

    def __init__(self, validation_results: dict[str, list[ValidationResults] | None]) -> None:
        self.validation_results = validation_results

    def display(self) -> None:
        """Generate an HTML report for validation results."""
        try:
            html_content = self._generate_validation_report_html()

            temp_report_path: pathlib.Path
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".html", encoding="utf-8"
            ) as temp_file:
                temp_file.write(html_content)
                temp_report_path = pathlib.Path(temp_file.name)

            resolved_temp_path = temp_report_path.resolve()
            console.print(f"📂 Report available at 👉: {resolved_temp_path.as_uri()}")
            webbrowser.open(resolved_temp_path.as_uri())

        except Exception as e:  # noqa: BLE001
            console.print(f"❌  Error generating report: {e.args}")

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

        all_reports = [
            report
            for reports_list in self.validation_results.values()
            if reports_list is not None
            for report in reports_list
        ]

        current_time_aware = datetime.datetime.now(datetime.UTC).astimezone()
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
            "css_content": css_content,
            "js_content": js_content,
        }
        return template.render(context)
