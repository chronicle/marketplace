from TIPCommon.extraction import (
    extract_job_param,
    extract_action_param,
    extract_configuration_param,
)

from ..core.config import Config


def prepare_report_comment(results: list[dict]) -> str:
    """
    Generates a comment using Suspicious and Malicious IOCs data

    :param results: ANY.RUN Sandbox analysis results
    :return: Complete comment
    """
    raws = ""

    for feed in results:
        if feed.get("reputation") in (1, 2):
            verdict = {1: "Suspiciuos", 2: "Malicious"}.get(feed.get("reputation"))
            raws += f"Type: {feed.get('type')} Value: {feed.get('ioc')} Verdict: {verdict}\n"

    return (
        "ANY.RUN Sandbox Indicators summary:\n" + raws
        if raws
        else "Suspiciuos or Malicious indicators not found"
    )


def prepare_base_params(siemplify) -> dict[str, str]:
    """Extracts analysis options"""
    return {
        "opt_timeout": extract_action_param(siemplify, param_name="opt_timeout"),
        "opt_network_connect": extract_action_param(siemplify, param_name="opt_network_connect"),
        "opt_network_fakenet": extract_action_param(siemplify, param_name="opt_network_fakenet"),
        "opt_network_tor": extract_action_param(siemplify, param_name="opt_network_tor"),
        "opt_network_geo": extract_action_param(siemplify, param_name="opt_network_geo"),
        "opt_network_mitm": extract_action_param(siemplify, param_name="opt_network_mitm"),
        "opt_network_residential_proxy": extract_action_param(
            siemplify, param_name="opt_network_residential_proxy"
        ),
        "opt_network_residential_proxy_geo": extract_action_param(
            siemplify, param_name="opt_network_residential_proxy_geo"
        ),
        "opt_privacy_type": extract_action_param(siemplify, param_name="opt_privacy_type"),
        "env_locale": extract_action_param(siemplify, param_name="env_locale"),
        "user_tags": extract_action_param(siemplify, param_name="user_tags"),
    }


def build_base_url(project_id: str, project_location: str, project_instance_id: str) -> str:
    """Generates SecOps API URL"""
    return f"https://{project_location}-chronicle.googleapis.com/v1alpha/projects/{project_id}/locations/{project_location}/instances/{project_instance_id}"


def build_sandbox_data_table_payload(data_table_name: str) -> dict:
    """
    Generates DataTable schema

    :param data_table_name: DataTable name
    :return: DataTable payload
    """
    return {
        "name": data_table_name,
        "display_name": data_table_name,
        "description": data_table_name,
        "column_info": [
            {
                "column_index": 0,
                "original_column": "value",
                "key_column": True,
                "column_type": "STRING",
            },
            {
                "column_index": 1,
                "original_column": "type",
                "key_column": True,
                "column_type": "STRING",
            },
            {
                "column_index": 2,
                "original_column": "confidence",
                "key_column": False,
                "column_type": "STRING",
            },
            {
                "column_index": 3,
                "original_column": "anyrun_task_url",
                "key_column": False,
                "column_type": "STRING",
            },
        ],
    }


def build_sandbox_indicators_payload(
    feeds: list[dict], task_uuid: str
) -> list[dict[str, str]] | None:
    """
    Converts ANY.RUN IOCs to the SecOps DataTable rows

    :param feeds: ANY.RUN Indicators
    :param task_uuid: ANY.RUN Sandbox analysis UUID
    :return: DataTable rows
    """
    payload = {"requests": []}

    for feed in feeds:
        if feed.get("reputation") in (1, 2):
            payload["requests"].append({
                "dataTableRow": {
                    "values": [
                        feed.get("ioc"),
                        feed.get("type"),
                        {1: "Suspiciuos", 2: "Malicious"}.get(feed.get("reputation")),
                        f"https://app.any.run/tasks/{task_uuid}",
                    ]
                }
            })

    return payload


def setup_action_proxy(siemplify) -> str | None:
    """Generates a proxy connection string"""
    if extract_configuration_param(
        siemplify, Config.INTEGRATION_NAME, param_name="Enable proxy", input_type=bool
    ):
        host = extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Proxy host"
        )
        port = extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Proxy port"
        )

        proxy_url = f"https://{host}:{port}"

        if extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Enable proxy auth", input_type=bool
        ):
            username = extract_configuration_param(
                siemplify, Config.INTEGRATION_NAME, param_name="Proxy username"
            )
            password = extract_configuration_param(
                siemplify, Config.INTEGRATION_NAME, param_name="Proxy password"
            )

            proxy_url = f"https://{username}:{password}@{host}:{port}"

        return proxy_url
