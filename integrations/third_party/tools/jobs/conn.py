from __future__ import annotations

import uuid

from soar_sdk.SiemplifyConnectorsDataModel import AlertInfo
from TIPCommon.base.connector import Connector
from TIPCommon.data_models import BaseAlert
from TIPCommon.extraction import extract_connector_param
from TIPCommon.validation import ParameterValidator


def main() -> None:
    ExampleConnector(script_name="Example Connector").start()


class ExampleConnector(Connector):
    def extract_params(self) -> None:
        self.params.alert_json = None
        self.params.alert_json_str = extract_connector_param(
            siemplify=self.siemplify,
            param_name="Alert JSON to ingest",
            is_mandatory=True,
            print_value=True,
        )

    def validate_params(self) -> None:
        validator: ParameterValidator = ParameterValidator(self.siemplify)
        self.params.alert_json = validator.validate_json(
            param_name="Alert JSON to ingest",
            json_string=self.params.alert_json_str,
        )

        self._validate_alert_json()

    def _validate_alert_json(self) -> None:
        match self.params.alert_json:
            case {"display_name": _, "events": [*_, _]} as alert_json if alert_json:
                return

            case _:
                msg: str = (
                    "Alert JSON to ingest is not a valid Alert object. "
                    "Please provide a valid JSON object with the following structure: "
                    "{'display_name': 'display_name', 'events': [...]}"
                )
                raise ValueError(msg)

    def init_managers(self) -> None:
        """No API requests needed for the connector."""

    def get_alerts(self) -> list[BaseAlert]:
        alert: BaseAlert = BaseAlert(
            raw_data=self.params.alert_json,
            alert_id=uuid.uuid4(),
        )
        return [alert]

    def create_alert_info(self, alert: BaseAlert) -> AlertInfo:
        alert_info: AlertInfo = AlertInfo()

        alert_info.alert_id = alert.alert_id
        alert_info.display_id = alert.raw_data["display_name"]
        alert_info.events = alert.raw_data["events"]

        return alert_info


if __name__ == "__main__":
    main()
