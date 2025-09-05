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

from urllib.parse import urljoin

import requests
from packaging import version
from requests.exceptions import HTTPError
from TIPCommon.rest.soar_api import (
    get_integration_instance_details_by_id,
    get_integration_instance_details_by_name,
    get_installed_integrations_of_environment,
    get_env_dynamic_parameters,
    get_domains,
    get_environments,
    import_environment,
    update_domain,
    get_environment_names,
    create_integrations_instance,
    save_integration_instance_settings,
    import_simulated_case,
    add_case_tag,
    add_case_stage,
    get_case_alert,
    add_close_reason,
    get_networks,
    update_network,
    get_custom_lists,
    update_custom_list,
    update_blocklist,
    update_sla_record,
    save_playbook,
)

VERSION_6117 = version.parse("6.1.17")
VERSION_6138 = version.parse("6.1.38.77")


class BaseUrlSession(requests.Session):
    # https://github.com/requests/toolbelt/blob/master/requests_toolbelt/sessions.py
    base_url = None

    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super(BaseUrlSession, self).__init__()

    def request(self, method, url, *args, **kwargs):
        url = self.create_url(url)
        return super(BaseUrlSession, self).request(method, url, *args, **kwargs)

    def create_url(self, url):
        return urljoin(self.base_url, url)


class SiemplifyApiClient:
    def __init__(
        self,
        api_root,
        api_key=None,
        smp_username=None,
        smp_password=None,
        use_ssl=False,
        siemplify_soar=None,
    ) -> None:
        self.api_root = f"{api_root}/external/v1/"
        self.api_key = api_key
        self.use_ssl = use_ssl
        self.session = BaseUrlSession(base_url=self.api_root)
        self.smp_username = smp_username
        self.smp_password = smp_password
        self.session.headers = {"AppKey": self.api_key}
        self.session.verify = use_ssl
        self._version = None
        self._bearer_token = None
        self.siemplify_soar = siemplify_soar
        if smp_username and smp_password:
            self._bearer_token = self.get_bearer_token(smp_password, smp_username)

    def get_bearer_token(self, smp_password, smp_username):
        payload = {"password": smp_password, "username": smp_username}
        res = self.session.post("auth/login", json=payload)
        self.validate_response(res)

        return f"Bearer {res.text}"

    @property
    def system_version(self):
        if not self._version:
            self._version = version.parse(self.get_system_version())
        return self._version

    def validate_response(self, response):
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise Exception(f"{e}: {response.content}")

    def test_connectivity(self):
        return bool(self.get_system_version())

    def get_page_results(self, url):
        payload = {"searchTerm": "", "requestedPage": 0, "pageSize": 100}
        res = self.session.post(url, json=payload)
        self.validate_response(res)
        results = res.json()["objectsList"]
        if res.json()["metadata"]["totalNumberOfPages"] > 1:
            for page in range(res.json()["metadata"]["totalNumberOfPages"] - 1):
                payload["requestedPage"] = page + 1
                res = self.session.post(url, json=payload)
                self.validate_response(res)
                results.extend(res.json()["objectsList"])
        return results

    def get_system_version(self):
        res = self.session.get("settings/GetSystemVersion")
        self.validate_response(res)
        return res.content.decode("utf-8").replace('"', "")

    def get_environment_names(self, siemplify):
        return get_environment_names(siemplify)

    def get_environment_group_names(self):
        res = self.session.get("environment-groups")
        self.validate_response(res)
        result = [f"({group['name']})" for group in res.json()["groups"]]
        return result

    def get_env_dynamic_parameters(
        self,
        siemplify
    ):
        return get_env_dynamic_parameters(
            siemplify
        )

    def add_dynamic_env_param(self, param):
        res = self.session.post("settings/AddOrUpdateDynamicParameters", json=param)
        self.validate_response(res)
        return res.content

    def get_store_data(self):
        store = self.session.get("store/GetIntegrationsStoreData")
        self.validate_response(store)
        powerups = self.session.get("store/GetPowerUpsStoreData")
        self.validate_response(powerups)
        return store.json()["integrations"] + powerups.json()["integrations"]

    def get_environments(self, siemplify):
        return get_environments(siemplify)

    def import_environment(self, siemplify, env_payload):
        return import_environment(siemplify, env_payload)

    def update_api_record(self, api_record):
        res = self.session.post("settings/addOrUpdateAPIKeyRecord", json=api_record)
        self.validate_response(res)

    def install_integration(
        self,
        integration_id,
        integration_version,
        is_certified=True,
    ):
        payload = {
            "name": integration_id,
            "identifier": integration_id,
            "version": integration_version,
            "isCertified": is_certified,
        }
        res = self.session.post(
            "store/DownloadAndInstallIntegrationFromLocalStore",
            json=payload,
        )
        self.validate_response(res)
        return True

    def export_package(self, integration):
        res = self.session.get(f"ide/ExportPackage/{integration}")
        self.validate_response(res)
        return res.content

    def import_package(self, integration_name, b64_blob):
        data = {
            "data": b64_blob,
            "integrationIdentifier": integration_name,
            "isCustom": True,
        }
        res = self.session.post("ide/ImportPackage", json=data)
        self.validate_response(res)
        return res.content

    def update_ide_item(self, input_json):
        res = self.session.post("ide/AddOrUpdateItem", json=input_json)
        self.validate_response(res)
        return res.json()

    def get_integrations_instances(self, siemplify, env):
        return get_installed_integrations_of_environment(
            chronicle_soar=siemplify,
            environment=env,
        )

    def get_integration_instance_settings(self, instance_id):
        res = self.session.get(
            f"integrations/GetIntegrationInstanceSettings/{instance_id}",
        )
        self.validate_response(res)
        return res.json()

    def create_integrations_instance(self, siemplify, integration, env):
        return create_integrations_instance(
            chronicle_soar=siemplify,
            integration_identifier=integration,
            environment=env,
        )

    def save_integration_instance_settings(self, siemplify, instance_identifier, env, settings):
        return save_integration_instance_settings(
            chronicle_soar=siemplify,
            identifier=instance_identifier,
            environment=env,
            integration_data=settings,
        )

    def get_ide_cards(self, include_staging=False):
        res = self.session.get("ide/GetIdeItemCards", verify=False)
        self.validate_response(res)
        if include_staging:
            return res.json()
        return [x for x in res.json() if not x.get("productionIntegrationIdentifier")]

    def get_ide_item(self, item_id, item_type):
        query = {"itemId": item_id, "ideItemType": item_type}
        res = self.session.post("ide/GetIdeItem", json=query, verify=False)
        self.validate_response(res)
        return res.json()

    def get_custom_families(self, include_default_vfs=False):
        res = self.session.get("ontology/GetVisualFamilies")
        self.validate_response(res)
        if include_default_vfs:
            return res.json()
        return [d for d in res.json() if d["isCustom"]]

    def get_custom_family(self, family_id):
        res = self.session.get(f"ontology/GetFamilyData/{family_id}")
        self.validate_response(res)
        return res.json()

    def add_custom_family(self, visual_family):
        res = self.session.post("ontology/AddOrUpdateVisualFamily", json=visual_family)
        self.validate_response(res)
        return res.content

    def get_ontology_records(self):
        return self.get_page_results("ontology/GetOntologyStatusRecords")

    def get_mapping_rules(self, source, product, event_name):
        payload = {"source": source, "product": product, "eventName": event_name}
        res = self.session.post("ontology/GetMappingRulesForSettings", json=payload)
        self.validate_response(res)
        return res.json()

    def add_mapping_rules(self, mapping_rule):
        res = self.session.post("ontology/AddOrUpdateMappingRules", json=mapping_rule)
        self.validate_response(res)
        return res.content

    def set_mappings_visual_family(self, source, product, event_name, visual_family):
        payload = {
            "source": source,
            "product": product or "",
            "eventName": event_name,
            "visualFamily": visual_family,
        }
        res = self.session.post(
            "ontology/AddOrUpdateProductToVisualizationFamilyRecord",
            json=payload,
        )
        self.validate_response(res)
        return True

    def get_playbooks(self):
        if self.system_version >= VERSION_6138:
            res = self.session.post(
                "playbooks/GetWorkflowMenuCardsWithEnvFilter",
                json=[0, 1],
            )
        else:
            res = self.session.post("playbooks/GetWorkflowMenuCards", json=[0, 1])
        self.validate_response(res)
        return res.json()

    def get_playbook(self, identifier):
        if self.system_version >= VERSION_6138:
            res = self.session.get(
                f"playbooks/GetWorkflowFullInfoWithEnvFilterByIdentifier/{identifier}",
            )
        else:
            res = self.session.get(
                f"playbooks/GetWorkflowFullInfoByIdentifier/{identifier}",
            )
        self.validate_response(res)
        return res.json()

    def export_playbooks(self, definitions):
        payload = {"identifiers": definitions}
        res = self.session.post("playbooks/ExportDefinitions", json=payload)
        self.validate_response(res)
        return res.content

    def import_playbooks(self, playbooks):
        res = self.session.post("playbooks/ImportDefinitions", json=playbooks)
        self.validate_response(res)
        return res.content

    def save_playbook(self, playbook):
        return save_playbook(self.siemplify_soar, playbook)

    def get_networks(self, siemplify):
        return get_networks(siemplify)

    def update_network(self, siemplify, network):
        return update_network(siemplify, network)

    def get_domains(self, siemplify):
        return get_domains(siemplify)

    def update_domain(self, siemplify, domain):
        return update_domain(siemplify, domain)

    def get_connectors(self, env_name=None):
        res = self.session.get("connectors/GetConnectorsData")
        self.validate_response(res)
        if env_name:
            connectors = []
            for connector in res.json()["installedConnectors"]:
                if connector["environment"] == env_name:
                    connectors.append(connector)
            return connectors
        return res.json()["installedConnectors"]

    def update_connector(self, connector_data):
        res = self.session.post("connectors/AddOrUpdateConnector", json=connector_data)
        self.validate_response(res)
        return res

    def get_custom_lists(self):
        return get_custom_lists(siemplify)

    def update_custom_list(self, siemplify, tracking_list, tracking_id=0):
        return update_custom_list(siemplify, tracking_list, tracking_id)

    def get_logo(self):
        res = self.session.get("settings/GetCompanyLogo")
        self.validate_response(res)
        return res.json()

    def update_logo(self, logo):
        res = self.session.post("settings/AddOrUpdateCompanyLogo", json=logo)
        self.validate_response(res)
        return True

    def get_case_title_settings(self):
        res = self.session.get("settings/GetCaseTitleSettings")
        self.validate_response(res)
        return res.json()

    def save_case_title_settings(self, settings):
        res = self.session.post("settings/SaveCaseTitleSettings", json=settings)
        self.validate_response(res)
        return True

    def get_case_stages(self):
        return self.get_page_results("settings/GetCaseStageDefinitionRecords")

    def add_case_stage(self, siemplify, stage):
        return add_case_stage(siemplify, stage)

    def get_email_templates(self):
        res = self.session.get("settings/GetEmailTemplateRecords")
        self.validate_response(res)
        return res.json()

    def add_email_template(self, template):
        res = self.session.post("settings/AddEmailTemplateRecords", json=template)
        self.validate_response(res)
        return True

    def get_denylists(self):
        if self.system_version > VERSION_6117:
            return self.get_blocklists()

        res = self.session.get("settings/GetAllModelBlackRecords")
        self.validate_response(res)
        return res.json()

    def update_denylist(self, siemplify, denylist):
        return self.update_blocklist(siemplify, denylist)

    # Version 6.1.17 +
    def get_blocklists(self):
        return self.get_page_results("settings/GetBlockListDetails")

    # Version 6.1.17 +
    def update_blocklist(self, siemplify, blocklist):
        res = update_blocklist(siemplify, blocklist)
        return res

    def get_sla_records(self):
        res = self.session.get("settings/GetSlaDefinitionsRecords")
        self.validate_response(res)
        return res.json()

    def update_sla_record(self, siemplify, definition):
        res = update_sla_record(siemplify, definition)
        return res

    def get_jobs(self):
        res = self.session.get("jobs/GetInstalledJobs")
        self.validate_response(res)
        return res.json()

    def add_job(self, job):
        res = self.session.post("jobs/SaveOrUpdateJobData", json=job)
        self.validate_response(res)
        return res.content

    def get_case_tags(self):
        return self.get_page_results("settings/GetTagDefinitionsRecords")

    def add_case_tag(self, siemplify, tag):
        return add_case_tag(siemplify, tag)

    def get_close_reasons(self, siemplify):
        return get_case_alert(siemplify)

    def add_close_reason(self, siemplify, cause):
        return add_close_reason(siemplify, cause)

    def create_playbook_category(self, name):
        req = {
            "categoryState": 0,  # Empty
            "id": 0,
            "isDefaultCategory": False,
            "name": name,
        }
        res = self.session.post("playbooks/AddOrUpdatePlaybookCategory", json=req)
        self.validate_response(res)
        return res.json()

    def get_playbook_categories(self):
        res = self.session.get("playbooks/GetWorkflowCategories")
        self.validate_response(res)
        return res.json()

    def get_simulated_cases(self):
        res = self.session.get("attackssimulator/GetCustomCases")
        self.validate_response(res)
        return res.json()

    def export_simulated_case(self, name):
        res = self.session.get(f"attackssimulator/ExportCustomCase/{name}")
        self.validate_response(res)
        return res.json()

    def import_simulated_case(self, siemplify, case):
        return import_simulated_case(siemplify, case)

    def get_integration_instance_name(
        self,
        chronicle_soar,
        integration_name: str,
        instance_id: str,
        environments,
    ) -> str | None:
        """Gets the integration instance name.

        Args:
            integration_name (str): Integration name.
            instance_id (str): Integration instance id.

        Returns:
            str: Returns display name of the integration instance.
        """
        res = get_integration_instance_details_by_id(
            chronicle_soar=chronicle_soar,
            integration_identifier=integration_name,
            instance_id=instance_id,
            environments=environments,
        )
        if res is None:
            return None

        return res.get("displayName") or res.get("instanceName")

    def get_integration_instance_id_by_name(
        self,
        chronicle_soar,
        integration_name: str,
        environments,
        display_name: str | None,
        consider_404_to_none: bool = False,
    ) -> str | None:
        """Gets the integration instance id by name.

        Args:
            integration_name (str): Integration name.
            display_name (str | None): Display name of the integration instance.
            consider_404_to_none (bool, optional): If True, treats HTTP 404 errors as None

        Returns:
            str | None: Returns integration instance id.
        """
        if display_name is None:
            return None

        try:
            res = get_integration_instance_details_by_name(
                chronicle_soar=chronicle_soar,
                integration_identifier=integration_name,
                instance_display_name=display_name,
                environments=environments,
            )
        except HTTPError as e:
            if e.response and e.response.status_code == 404 and consider_404_to_none:
                return None

            raise

        if res is None:
            return None

        return res.get("identifier")
