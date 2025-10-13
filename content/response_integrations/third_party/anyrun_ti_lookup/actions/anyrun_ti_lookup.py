import json
from base64 import b64encode

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from TIPCommon.rest.soar_api import save_attachment_to_case_wall
from TIPCommon.data_models import CaseWallAttachment
from TIPCommon.extraction import extract_action_param, extract_configuration_param

from ..core.config import Config
from ..core.utils import (
    setup_action_proxy,
    convert_score,
    prepare_report_comment,
    generate_lookup_reference,
)

from anyrun.connectors import LookupConnector


def initialize_lookup(
    siemplify, token: str, lookup_entity: str, entity_identifier: str, lookup_depth: int
) -> str:
    with LookupConnector(
        token, integration=Config.VERSION, proxy=setup_action_proxy(siemplify)
    ) as connector:
        report = connector.get_intelligence(
            lookup_depth=lookup_depth, **{lookup_entity: entity_identifier}
        )

        siemplify.add_comment(
            f"Lookup url: {generate_lookup_reference(lookup_entity, entity_identifier)}"
        )
        save_attachment_to_case_wall(
            siemplify,
            CaseWallAttachment(
                f"{entity_identifier[:15]}_anyrun_lookup_summary",
                ".json",
                b64encode(json.dumps(report).encode()).decode(),
                True,
            ),
        )

        return convert_score(report.get("summary"))


@output_handler
def main():
    siemplify = SiemplifyAction()
    results = []

    lookup_depth = siemplify.extract_action_param("lookup_depth", input_type=int)

    token = extract_configuration_param(
        siemplify,
        Config.INTEGRATION_NAME,
        param_name="ANY.RUN TI Lookup API KEY",
        is_mandatory=True,
    )

    if query := siemplify.extract_action_param("query"):
        verdict = initialize_lookup(siemplify, token, "query", query, lookup_depth)
        results.append(("Query", "query", verdict))
    else:
        entity_identifiers = siemplify.extract_action_param("identifiers")
        entity_types = siemplify.extract_action_param("types")

        if not any([entity_identifiers, entity_types]):
            siemplify.end(
                "At least one entity type and entity identifiers must be specified",
                False,
                EXECUTION_STATE_FAILED,
            )

        entity_identifiers = entity_identifiers.split(",")
        entity_types = entity_types.split(",")

        for entity_type, entity_identifier in zip(entity_types, entity_identifiers):
            if lookup_entity := Config.ENTITIES.get(entity_type.lower()):
                verdict = initialize_lookup(
                    siemplify, token, lookup_entity, entity_identifier, lookup_depth
                )
                siemplify.LOGGER.info(
                    f"Entity: entity_identifier was lookuped. Json summary attached to the case wall."
                )
                results.append((entity_type, entity_identifier, verdict))
            else:
                siemplify.LOGGER.info(f"Recieved not supported entity type: {entity_type}")
                results.append((entity_type, entity_identifier, "Not supported entity"))

    siemplify.add_comment(prepare_report_comment(results))
    siemplify.end(f"Intelligence is successfully ended.", False, EXECUTION_STATE_COMPLETED)


if __name__ == "__main__":
    main()
