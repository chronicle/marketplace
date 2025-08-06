from __future__ import annotations

from TIPCommon.base.action import EntityTypesEnum
from TIPCommon.base.action.base_enrich_action import EnrichAction
from TIPCommon.base.action.data_models import DataTable, Entity
from TIPCommon.extraction import extract_action_param
from TIPCommon.transformation import add_prefix_to_dict, construct_csv
from TIPCommon.validation import ParameterValidator
from soar_sdk.SiemplifyUtils import unix_now

from ..core.base_action import BaseAction
from ..core.constants import (
    ENRICH_ENTITY_ACTION_EXAMPLE_SCRIPT_NAME,
    SupportedEntitiesEnum,
)


DEFAULT_ENTITY_TYPE: str = SupportedEntitiesEnum.ALL.value

SUCCESS_MESSAGE: str = "Successfully enriched the following entities: {}"
NO_ENTITIES_MESSAGE: str = "No eligible entities were found in the scope of the Alert."


class EnrichEntityActionExample(EnrichAction, BaseAction):

    def __init__(self) -> None:
        super().__init__(ENRICH_ENTITY_ACTION_EXAMPLE_SCRIPT_NAME)
        self.enriched_entities: list[str] = []

    def _extract_action_parameters(self) -> None:
        self.params.entity_type = extract_action_param(
            self.soar_action,
            param_name="Entity Type",
            default_value=DEFAULT_ENTITY_TYPE,
            print_value=True,
        )

    def _validate_params(self) -> None:
        validator = ParameterValidator(self.soar_action)
        self.params.entity_type = validator.validate_ddl(
            param_name="Entity Type",
            value=self.params.entity_type,
            ddl_values=SupportedEntitiesEnum.values(),
            print_value=True,
        )

    def _get_entity_types(self) -> list[EntityTypesEnum]:
        return SupportedEntitiesEnum(self.params.entity_type).to_entity_type_enum_list()

    def _perform_enrich_action(self, current_entity: Entity) -> None:
        self.logger.info(f"Starting enrichment for entity {current_entity.identifier}")
        timestamp = unix_now()

        enrichment_data = {
            "enriched": "true",
            "timestamp": str(timestamp),
        }
        self.enrichment_data = add_prefix_to_dict(enrichment_data, "SampleIntegration_")
        self.entity_results = enrichment_data
        self.data_tables = [
            DataTable(
                title=f"Sample: {current_entity.identifier}",
                data_table=construct_csv([enrichment_data]),
            )
        ]
        self.enriched_entities.append(current_entity.identifier)
        self.logger.info(f"Finished enrichment for entity {current_entity.identifier}")

    def _finalize_action_on_success(self) -> None:
        super()._finalize_action_on_success()
        if self.enriched_entities:
            self.output_message = SUCCESS_MESSAGE.format(
                ", ".join(self.enriched_entities)
            )
        else:
            self.output_message = NO_ENTITIES_MESSAGE
            self.result_value = False


def main():
    EnrichEntityActionExample().run()


if __name__ == "__main__":
    main()
