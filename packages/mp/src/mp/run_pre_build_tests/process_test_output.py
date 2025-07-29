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

import json
import pathlib

import rich


class TestIssue:
    def __init__(self, test_name: str, stack_trace: str) -> None:
        self.test_name: str = test_name
        self.stack_trace: str = stack_trace


class IntegrationTestResults:
    def __init__(self, integration_name: str) -> None:
        self.integration_name: str = integration_name
        self.failed_tests: int = 0
        self.skipped_tests: int = 0
        self.failed_tests_summary: list[TestIssue] = []
        self.skipped_tests_summary: list[TestIssue] = []


def process_pytest_json_report(
    integration_name: str, json_report_path: pathlib.Path
) -> IntegrationTestResults:
    """Processes the parsed JSON report data from pytest-json and returns an IntegrationTestResults object.

    Args:
        integration_name: The name of the integration being tested.
        json_report_path: The path to the pytest JSON report file.

    Returns:
        An IntegrationTestResults object containing extracted information about
        test counts, and details of failed tests.

    """
    report_data = {}
    try:
        with open(json_report_path, encoding="utf-8") as f:
            report_data = json.load(f)

        json_report_path.unlink(missing_ok=True)

    except FileNotFoundError:
        rich.print(f"[bold red]Error:[/bold red] JSON report not found at {json_report_path}")
        return IntegrationTestResults(integration_name)
    except json.JSONDecodeError as e:
        rich.print(
            f"[bold red]Error:[/bold red] Failed to decode JSON report at {json_report_path}: {e}"
        )
        json_report_path.unlink(missing_ok=True)
        return IntegrationTestResults(integration_name)

    integration_results = IntegrationTestResults(integration_name=integration_name)

    summary = report_data.get("summary", {})
    integration_results.skipped_tests = summary.get("skipped", 0)

    for test_item in report_data.get("tests", []):
        outcome = test_item.get("outcome")
        if outcome == "failed":
            issue = _extract_failed_test_issue(test_item)
            integration_results.failed_tests_summary.append(issue)
        elif outcome == "skipped":
            issue = _extract_skipped_test_issue(test_item)
            integration_results.skipped_tests_summary.append(issue)

    integration_results.failed_tests = len(integration_results.failed_tests_summary)

    return integration_results


def _extract_failed_test_issue(test_item: dict) -> TestIssue:
    """Extracts relevant information for a failed test item and returns a TestIssue."""
    test_name: str = test_item.get("nodeid", "N/A")
    call_info = test_item.get("call", {})
    full_stack_trace = "No stack trace available"

    longrepr = call_info.get("longrepr")
    if isinstance(longrepr, str):
        full_stack_trace = longrepr
    elif isinstance(longrepr, dict):
        if "reprtraceback" in longrepr and "content" in longrepr["reprtraceback"]:
            full_stack_trace = longrepr["reprtraceback"]["content"]
        elif "sections" in longrepr:
            for section in longrepr["sections"]:
                if section[0].startswith("____ "):
                    full_stack_trace = section[1]
                    break

    return TestIssue(test_name=test_name, stack_trace=full_stack_trace)


def _extract_skipped_test_issue(test_item: dict) -> TestIssue:
    """Extracts relevant information for a skipped test item and returns a TestIssue."""
    test_name: str = test_item.get("nodeid", "N/A")
    skip_reason = test_item.get("was_skipped", "Unknown reason").strip()

    if not skip_reason or skip_reason == "Unknown reason":
        call_info = test_item.get("call", {})
        longrepr = call_info.get("longrepr")
        if isinstance(longrepr, str):
            skip_reason = longrepr.splitlines()[0] if longrepr else "No specific reason found."
        elif isinstance(longrepr, dict) and "reprcrash" in longrepr:
            skip_reason = longrepr["reprcrash"].get("message", "No specific reason found.")
        elif isinstance(longrepr, dict) and "sections" in longrepr:
            for section in longrepr["sections"]:
                if "skip" in section[0].lower() or "skipped" in section[0].lower():
                    skip_reason = section[1].splitlines()[0] if section[1] else skip_reason
                    break

    return TestIssue(test_name=test_name, stack_trace=skip_reason)
