from __future__ import annotations

import datetime
import pathlib
import sys

from integration_testing.common import set_is_test_run_to_true
from integration_testing.platform.external_context import (
    ExternalContextRowKey,
    MockExternalContext,
)
from integration_testing.platform.script_output import MockConnectorOutput
from integration_testing.set_meta import set_metadata
from TIPCommon.data_models import DatabaseContextType
from TIPCommon.types import SingleJson
from TIPCommon.utils import is_test_run

from sample_integration.connectors.simple_connector_example import SimpleConnector
from sample_integration.tests.common import CONFIG, INTEGRATION_PATH, MOCK_RATES_DEFAULT
from sample_integration.tests.core.product import VatComply
from sample_integration.tests.core.session import VatComplySession

IDS_DB_KEY: str = "offset"
DEF_PATH: pathlib.Path = INTEGRATION_PATH / "connectors" / "simple_connector_example.yaml"

DEFAULT_PARAMETERS: SingleJson = {
    "Environment Field Name": "Default Environment",
    "Run Every": 10,
    "DeviceProductField": "device_product",
    "EventClassId": "event_name",
    "API Root": CONFIG.get("API Root"),
    "Password Field": CONFIG.get("Password Field"),
    "Verify SSL": "false",
    "Max Days Backwards": "3",
    "Max Alerts To Fetch": "3",
    "Currencies To Fetch": "EUR",
}
ALERT_NAME: str = "Microsoft Graph Monitored Mailbox <>"


@set_metadata(connector_def_file_path=DEF_PATH, parameters=DEFAULT_PARAMETERS)
def test_simeple_connector_example_connector(
    vatcomply: VatComply,
    script_session: VatComplySession,
    connector_output: MockConnectorOutput,
) -> None:
    today = datetime.date.today().isoformat()
    MOCK_RATES_DEFAULT["date"] = today
    vatcomply.set_rates(MOCK_RATES_DEFAULT)

    set_is_test_run_to_true()
    is_test = is_test_run(sys.argv)
    connector = SimpleConnector(is_test)
    connector.start()

    assert len(script_session.request_history) == 7
    assert connector_output.results.json_output.alerts[0].name == ALERT_NAME


@set_metadata(connector_def_file_path=DEF_PATH, parameters=DEFAULT_PARAMETERS)
def test_simeple_connector_example_with_no_external_context(
    vatcomply: VatComply,
    script_session: VatComplySession,
    connector_output: MockConnectorOutput,
    external_context: MockExternalContext,
) -> None:
    today = datetime.date.today().isoformat()
    MOCK_RATES_DEFAULT["date"] = today
    vatcomply.set_rates(MOCK_RATES_DEFAULT)

    set_is_test_run_to_true()
    is_test = is_test_run(sys.argv)
    connector = SimpleConnector(is_test)
    connector.start()

    assert len(script_session.request_history) == 7
    assert connector_output.results.json_output.alerts[0].name == ALERT_NAME
    assert len(connector_output.results.json_output.alerts) == 1

    row_key: ExternalContextRowKey = ExternalContextRowKey(
        context_type=DatabaseContextType.CONNECTOR,
        property_key=IDS_DB_KEY,
        identifier=None,
    )
    assert row_key not in external_context
