"""Core constants that can be used across multiple apps/components."""

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

REPO_NAME: str = "marketplace"

PROJECT_FILE: str = "pyproject.toml"
INTEGRATIONS_DIR_NAME: str = "integrations"
COMMUNITY_DIR_NAME: str = "third_party"
COMMERCIAL_DIR_NAME: str = "commercial"
OUT_INTEGRATIONS_DIR_NAME: str = "integrations"
OUT_DIR_NAME: str = "out"
REQUIREMENTS_FILE: str = "requirements.txt"
INTEGRATION_DEF_FILE: str = "Integration-{0}.def"
INTEGRATION_FULL_DETAILS_FILE: str = "{0}.fulldetails"
RN_JSON_FILE: str = "RN.json"
OUT_DEPENDENCIES_DIR: str = "Dependencies"
INTEGRATION_VENV: str = ".venv"
MARKETPLACE_JSON_NAME: str = "marketplace.json"

OUT_ACTIONS_META_DIR: str = "ActionsDefinitions"
OUT_CONNECTORS_META_DIR: str = "Connectors"
OUT_JOBS_META_DIR: str = "Jobs"
OUT_WIDGETS_META_DIR: str = "Widgets"

ACTIONS_META_SUFFIX: str = ".actiondef"
CONNECTORS_META_SUFFIX: str = ".connectordef"
JOBS_META_SUFFIX: str = ".jobdef"
WIDGETS_META_SUFFIX: str = ".json"
DEF_FILE_SUFFIX: str = ".yaml"

OUT_ACTION_SCRIPTS_DIR: str = "ActionsScripts"
OUT_CONNECTOR_SCRIPTS_DIR: str = "ConnectorsScripts"
OUT_JOB_SCRIPTS_DIR: str = "JobsScrips"
OUT_WIDGET_SCRIPTS_DIR: str = "WidgetsScripts"
OUT_MANAGERS_SCRIPTS_DIR: str = "Managers"
OUT_CUSTOM_FAMILIES_DIR: str = "DefaultCustomFamilies"
OUT_CUSTOM_FAMILIES_FILE: str = "integration_families.json"
OUT_MAPPING_RULES_DIR: str = "DefaultMappingRules"
OUT_MAPPING_RULES_FILE: str = "integration_mapping_rules.json"

CUSTOM_FAMILIES_FILE: str = f"integration_families{DEF_FILE_SUFFIX}"
MAPPING_RULES_FILE: str = f"integration_mapping_rules{DEF_FILE_SUFFIX}"
ACTIONS_DIR: str = "actions"
CONNECTORS_DIR: str = "connectors"
JOBS_DIR: str = "jobs"
WIDGETS_DIR: str = "widgets"
TESTS_DIR: str = "tests"
CORE_SCRIPTS_DIR: str = "core"
PACKAGE_FILE: str = "__init__.py"
COMMON_SCRIPTS_DIR: str = "group_modules"
DEFINITION_FILE: str = f"definition{DEF_FILE_SUFFIX}"
RELEASE_NOTES_FILE: str = f"release_notes{DEF_FILE_SUFFIX}"
SDK_PACKAGE_NAME: str = "soar_sdk"

README_FILE: str = "README.md"
LOCK_FILE: str = "uv.lock"
PYTHON_VERSION_FILE: str = ".python-version"

MS_IN_SEC: int = 1_000

EXCLUDED_INTEGRATIONS_IDS_WITHOUT_PING: set[str] = {
    "ChronicleSupportTools",
    "Connectors",
    "Lacework",
    "PagerDuty",
}
LONG_DESCRIPTION_MAX_LENGTH: int = 2_200
SHORT_DESCRIPTION_MAX_LENGTH: int = 400
DISPLAY_NAME_MAX_LENGTH: int = 150
MAX_PARAMETERS_LENGTH: int = 50
MINIMUM_SCRIPT_VERSION: float = 1.0
# language=regexp
SCRIPT_DISPLAY_NAME_REGEX: str = (
    r"^[a-zA-Z0-9-\s]+$"
    # Excluded scripts that already have issues with their name
    r"|^IOC_Enrichment$"
)
# language=regexp
SCRIPT_IDENTIFIER_REGEX: str = (
    r"^[a-zA-Z0-9-_]+$"
    # Excluded integrations that already have blank spaces in their identifier
    r"|^Bitdefender GravityZone$"
    r"|^Cybersixgill Actionable Alerts$"
    r"|^Full Contact$"
    r"|^IPQS Fraud and Risk Scoring$"
    r"|^Cybersixgill DVE Feed$"
    r"|^Google Safe Browsing$"
    r"|^WHOIS XML API$"
    r"|^Google Docs$"
    r"|^AWS - EC2$"
    r"|^Google Sheets$"
    r"|^Google Drive$"
    r"|^Bandura Cyber$"
    r"|^Luminar IOCs and Leaked Credentials$"
    r"|^Docker Hub$"
    r"|^Azure DevOps$"
    r"|^Cybersixgill Darkfeed$"
    r"|^Cybersixgill DVE Enrichment$"
    r"|^Spell Checker$"
    r"|^Cybersixgill Darkfeed Enrichment$"
    r"|^Workflow Tools$"
)
# language=regexp
PARAM_DISPLAY_NAME_REGEX: str = (
    r"^[a-zA-Z0-9-'\s]+$"
    # Excluded parameters that already have issues with their name
    r"|^Verify SSL Ceritifcate\?$"
    r"|^Git Password/Token/SSH Key$"
    r"|^EML/MSG Base64 String$"
    r"|^Country\(For multiple countries, provide comma-separated values\)$"
    r"|^Entity Identifier\(s\)$"
    r"|^logzio_security_token$"
    r"|^logzio_region$"
    r"|^minimum_score$"
    r"|^api_token$"
    r"|^eyeglass_ip$"
    r"|^API_Key$"
    r"|^Alert_ID$"
    r"|^Queue_State$"
    r"|^logzio_operations_token$"
    r"|^logzio_custom_endpoint$"
    r"|^api_key$"
    r"|^fields_to_search$"
    r"|^severity_threshold$"
    r"|^Entity Identifier\(s\) Type$"
    r"|^Target Entity Identifier\(s\)$"
    r"|^IOC_Enrichment$"
    r"|^SLA \(in minutes\)$"
    r"|^raw_json$"
    r"|^alert_event_id$"
    r"|^Additional_Data$"
    r"|^page_size$"
    r"|^sort_by$"
    r"|^Data_Range$"
    r"|^Incident_Key$"
    r"|^Team_IDS$"
    r"|^User_IDS$"
    r"|^Service_IDS$"
    r"|^Entity_State$"
    r"|^Incidents_Statuses$"
    r"|^from_time$"
    r"|^to_time$"
    r"|^Incident_ID$"
    r"|^from_date$"
    r"|^logzio_token$"
    r"|^search_term$"
)
