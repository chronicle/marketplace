from anyrun import RunTimeException
from anyrun.connectors import FeedsConnector, LookupConnector
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import output_handler
from TIPCommon.extraction import extract_configuration_param

from ..core.config import Config


@output_handler
def main():
    siemplify = SiemplifyAction()
    siemplify.script_name = f"{Config.INTEGRATION_NAME} - Ping"

    lookup_token = extract_configuration_param(
        siemplify,
        Config.INTEGRATION_NAME,
        param_name="ANY.RUN TI Lookup API KEY",
        is_mandatory=True,
    )

    try:
        if extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Enable proxy", input_type=bool
        ):
            check_proxy(siemplify, lookup_token)

        with LookupConnector(api_key=lookup_token, integration=Config.VERSION) as connector:
            connector.check_authorization()

    except RunTimeException as exception:
        output_message = str(exception)
        siemplify.LOGGER.error(output_message)
        status = EXECUTION_STATE_FAILED
        is_succes = False
    else:
        output_message = (
            f"[ANY.RUN] Successful connection to the {Config.INTEGRATION_NAME} services!"
        )
        siemplify.LOGGER.info(output_message)
        status = EXECUTION_STATE_COMPLETED
        is_succes = True

    siemplify.end(output_message, is_succes, status)


def check_proxy(siemplify: SiemplifyAction, token: str) -> None:
    try:
        host = extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Proxy host"
        )
        port = extract_configuration_param(
            siemplify, Config.INTEGRATION_NAME, param_name="Proxy port"
        )

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
        else:
            proxy_url = f"https://{host}:{port}"

        with FeedsConnector(api_key=token, proxy=proxy_url) as connector:
            connector.check_proxy()

    except TypeError:
        raise RunTimeException(
            "[ANY.RUN] The proxy request failed. Check the proxy settings are correct"
        )


if __name__ == "__main__":
    main()
