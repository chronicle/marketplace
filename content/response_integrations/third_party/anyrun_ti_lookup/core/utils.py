from TIPCommon.extraction import extract_configuration_param

from ..core.config import Config


def generate_lookup_reference(artifact_type: str, artifact_value: str) -> str:
    """ Generates ANY.RUN TI Lookup hyperlink """
    return 'https://intelligence.any.run/analysis/lookup#{%22query%22:%22' + artifact_type + ':%5C%22' + artifact_value + '%5C%22%22,%22dateRange%22:90}'


def convert_score(report: dict | None) -> str:
    """
    Converts ANY.RUN TI Lookup verdict to the text status

    :param report: ANY.RUN TI Lookup summary
    :return: Text verdict
    """
    if not report:
        return 'No info'
    
    if score := report.get('threatLevel'):
        if score == 1:
            return 'Suspicious'
        elif score == 2:
            return 'Malicious'
        else:
            return 'Unknown'

    return 'No info'


def prepare_report_comment(results: list[tuple[str, str, str]]) -> str:
    """
    Generates a comment using Suspicious and Malicious IOCs data

    :param results: ANY.RUN TI Lookup results
    :return: Complete comment
    """
    raws = '\n'.join(f'Type: {result[0]} Value: {result[1]} Verdict: {result[2]}' for result in results)
    return 'ANY.RUN TI Lookup summary:\n' + raws


def setup_action_proxy(siemplify) -> str | None:
    """ Generates a proxy connection string """
    if extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Enable proxy', input_type=bool):
        host = extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Proxy host')
        port = extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Proxy port')

        proxy_url = f"https://{host}:{port}"

        if extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Enable proxy auth', input_type=bool):
            username = extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Proxy username')
            password = extract_configuration_param(siemplify, Config.INTEGRATION_NAME, param_name='Proxy password')

            proxy_url = f"https://{username}:{password}@{host}:{port}"

        return proxy_url
