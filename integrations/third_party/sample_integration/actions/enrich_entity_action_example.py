from TIPCommon.base.action import EntityTypesEnum
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


DEFAULT_ENTITY_TYPE = SupportedEntitiesEnum.ALL.value

SUCCESS_MESSAGE = "Successfully enriched the following entities: {}"
NO_ENTITIES_MESSAGE = "No eligible entities were found in the scope of the Alert."


class EnrichEntityActionExample(BaseAction):

    def __init__(self) -> None:
        super().__init__(ENRICH_ENTITY_ACTION_EXAMPLE_SCRIPT_NAME)
        self.enriched_entities: list[str] = []
        self.error_output_message: str = (
            f'Error executing action "{ENRICH_ENTITY_ACTION_EXAMPLE_SCRIPT_NAME}".'
        )

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

    def _enrich_entity(self, entity: Entity):
        """Enrich a single entity with sample data."""
        timestamp = unix_now()

        enrichment_data = {
            "enriched": "true",
            "timestamp": str(timestamp),
        }
        entity.additional_properties.update(
            add_prefix_to_dict(enrichment_data, "SampleIntegration_")
        )
        entity.is_enriched = True
        self.entities_to_update.append(entity)
        return enrichment_data

    def _finalize_action_on_success(self) -> None:
        super()._finalize_action_on_success()
        self.output_message = SUCCESS_MESSAGE.format(", ".join(self.enriched_entities))

    def _perform_action(self, entity: Entity):
        enrichment_data = self._enrich_entity(entity)
        self.logger.info(f"Successfully enriched entity {entity.identifier}")
        self.enriched_entities.append(entity.identifier)
        self.json_results[entity.identifier] = enrichment_data
        self.data_tables.append(
            DataTable(
                title=f"Sample: {entity.identifier}",
                data_table=construct_csv([enrichment_data]),
            )
        )


def main():
    EnrichEntityActionExample().run()


if __name__ == "__main__":
    main()
