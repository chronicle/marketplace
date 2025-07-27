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
        """Generate an HTML report with dual behavior:

        - Locally: Saves to a temp file and opens in a browser.
        - In GitHub Actions: Saves to a predictable path for artifact upload.
        """
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
            console.print("✅ Report successfully generated.")
            console.print(f"📂 Report available at: {resolved_path.as_uri()}")

            if not is_github_actions:
                console.print("🚀 Opening report in your default web browser...")
                webbrowser.open(resolved_path.as_uri())
            else:
                console.print(f"Artifact path for CI: {resolved_path}")

        except Exception as e:
            console.print(f"❌ Error generating report: {e}")

    def _generate_validation_report_html(self, template_name: str = "report_template.html") -> str:
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
        context = {
            "reports_by_category": self.validation_results,
            "total_integrations": len(all_reports),
            "total_passed": sum(
                1
                for r in all_reports
                if not r.validation_report.failed_fatal_validations
                and not r.validation_report.failed_non_fatal_validations
            ),
            "total_fatal_issues": sum(
                len(r.validation_report.failed_fatal_validations) for r in all_reports
            ),
            "total_non_fatal_issues": sum(
                len(r.validation_report.failed_non_fatal_validations) for r in all_reports
            ),
            "current_time": datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        }
        return template.render(context)
