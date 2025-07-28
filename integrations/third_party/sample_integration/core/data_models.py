from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime

from soar_sdk.SiemplifyConnectorsDataModel import AlertInfo
from TIPCommon.transformation import dict_to_flat
from TIPCommon.types import SingleJson

import constants
from core.utils import create_secops_attachment_object


@dataclass(frozen=True, slots=True)
class BaseRate:
    base: str
    date: str
    rates: SingleJson

    def json(self) -> SingleJson:
        return {"base": self.base, "rates": self.rates}

    def to_csv(self) -> list[SingleJson]:
        return [
            {"Currency": symbol, "Value": value} for symbol, value in self.rates.items()
        ]

    def to_alerts(
        self,
        create_per_rate: bool,
        severity: str,
        env_common,
    ) -> list[AlertInfo]:
        if create_per_rate:
            return [
                self._build_alert(currency, rate, severity, env_common)
                for currency, rate in self.rates.items()
            ]
        return [self._build_combined_alert(severity, env_common)]

    def _build_alert(
        self,
        currency: str,
        rate: float,
        severity: str,
        env_common,
    ) -> AlertInfo:
        alert = AlertInfo()
        alert.display_id = self._format_exchange_display_id(currency)
        alert.ticket_id = alert.display_id
        alert.name = self._format_exchange_alert_name(currency)
        alert.events = [self._build_event(currency, rate)]
        attachment_content = json.dumps(
            {"base": self.base, "date": self.date, "rates": {currency: rate}}
        )
        alert.attachments = [
            create_secops_attachment_object(
                file_name=alert.display_id,
                file_content=attachment_content.encode(),
            )
        ]
        self._populate_common_alert_fields(alert, severity, env_common)
        return alert

    def _build_combined_alert(self, severity: str, env_common) -> AlertInfo:
        alert = AlertInfo()
        alert.display_id = self._format_display_id()
        alert.ticket_id = alert.display_id
        alert.name = self._format_alert_name()
        alert.events = [
            self._build_event(currency, rate) for currency, rate in self.rates.items()
        ]
        alert.attachments = [self.json()]
        attachment_content = json.dumps(self.json())
        alert.attachments = [
            create_secops_attachment_object(
                file_name=alert.display_id,
                file_content=attachment_content.encode(),
            )
        ]
        self._populate_common_alert_fields(alert, severity, env_common)
        return alert

    def _build_event(self, currency: str, rate: float) -> dict:
        return dict_to_flat(
            {"date": self.date, "base": self.base, "rates": {currency: rate}}
        )

    def _populate_common_alert_fields(
        self,
        alert: AlertInfo,
        severity: str,
        env_common,
    ) -> None:
        timestamp = self._get_timestamp()
        alert.description = constants.DESCRIPTION
        alert.alert_id = alert.display_id
        alert.reason = constants.REASON
        alert.device_vendor = constants.DEFAULT_VENDOR
        alert.device_product = constants.DEFAULT_PRODUCT
        alert.rule_generator = constants.RULE_GENERATOR
        alert.priority = constants.AlertSeverityEnum(severity).severity
        alert.environment = env_common.get_environment(self._env_data())
        alert.start_time = alert.end_time = timestamp
        alert.source_grouping_identifier = (
            constants.SOURCE_GROUPING_IDENTIFIER_FORMAT.format(
                date=self.date, base=self.base
            )
        )

    def _format_display_id(self) -> str:
        return constants.DISPLAY_ID_FORMAT.format(date=self.date, base=self.base)

    def _format_exchange_display_id(self, currency: str) -> str:
        return constants.DISPLAY_ID_EXCHANGE_FORMAT.format(
            date=self.date, base=self.base, currency=currency
        )

    def _format_alert_name(self) -> str:
        return constants.ALERT_NAME_FORMAT.format(date=self.date, base=self.base)

    def _format_exchange_alert_name(self, currency: str) -> str:
        return constants.ALERT_NAME_EXCHANGE_FORMAT.format(
            date=self.date, base=self.base, currency=currency
        )

    def _get_timestamp(self) -> int:
        return int(datetime.strptime(self.date, "%Y-%m-%d").timestamp()) * 1000

    def _env_data(self) -> SingleJson:
        return dict_to_flat(
            {
                "date": self.date,
                "base": self.base,
                "rates": self.rates,
            }
        )


@dataclass(frozen=True, slots=True)
class DailyRates:
    date: str
    exchange_rates: list[BaseRate]

    def json(self) -> SingleJson:
        return {
            "date": self.date,
            "exchange_rates": [rate.json() for rate in self.exchange_rates],
        }
