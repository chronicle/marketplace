from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED
from TIPCommon.extraction import extract_action_param, extract_configuration_param
from TIPCommon.rest.soar_api import save_attachment_to_case_wall
from TIPCommon.data_models import CaseWallAttachment
from base64 import b64encode

from ..core.utils import prepare_base_params, setup_action_proxy, prepare_report_comment
from ..core.data_table_manager import DataTableManager
from ..core.config import Config

from anyrun.connectors import SandboxConnector


@output_handler
def main():
    siemplify = SiemplifyAction()

    token = extract_configuration_param(
        siemplify, Config.INTEGRATION_NAME, param_name="ANY.RUN Sandbox API KEY", is_mandatory=True
    )

    urls = extract_action_param(siemplify, param_name="url", is_mandatory=True)

    if not urls:
        siemplify.end("Destination URL is not found.", False, EXECUTION_STATE_FAILED)

    for obj_url in urls.split(","):
        with SandboxConnector.android(
            token, integration=Config.VERSION, proxy=setup_action_proxy(siemplify)
        ) as connector:
            task_uuid = connector.run_url_analysis(
                obj_url=obj_url, **prepare_base_params(siemplify)
            )

            siemplify.add_comment(
                f"Link to the ANY.RUN interactive analysis: https://app.any.run/tasks/{task_uuid}"
            )

            for status in connector.get_task_status(task_uuid):
                siemplify.LOGGER.info(status)

            report = connector.get_analysis_report(task_uuid, report_format="html")

            save_attachment_to_case_wall(
                siemplify,
                CaseWallAttachment(
                    f"{obj_url[:15]}_anyrun_sandbox_report",
                    ".html",
                    b64encode(report.encode()).decode(),
                    True,
                ),
            )

            if iocs := connector.get_analysis_report(task_uuid, report_format="ioc"):
                data_tables = DataTableManager(siemplify)
                data_tables.update_sandbox_indicators(iocs, task_uuid)
                siemplify.add_comment(prepare_report_comment(iocs))

            status = connector.get_analysis_verdict(task_uuid)
            siemplify.add_comment(
                f"URL analysis for the entity:\n{obj_url} is successfully ended.\nAnalysis status: {status}."
            )

    siemplify.end(f"URL analysis is successfully ended.", False, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
