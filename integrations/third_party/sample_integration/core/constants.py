import datetime
from enum import Enum
from typing import Mapping

from TIPCommon.base.action import EntityTypesEnum

# Integration Identifiers
INTEGRATION_IDENTIFIER = "SampleIntegration"
INTEGRATION_DISPLAY_NAME = "Sample Integration"

# Script Identifiers
PING_SCRIPT_NAME = f"{INTEGRATION_IDENTIFIER} - Ping"
SIMPLE_ACTION_EXAMPLE_SCRIPT_NAME = f"{INTEGRATION_IDENTIFIER} - Simple Action Example"
ENRICH_ENTITY_ACTION_EXAMPLE_SCRIPT_NAME = (
    f"{INTEGRATION_IDENTIFIER} - Enrich Entity Action Example"
)
ASYNC_ACTION_EXAMPLE_SCRIPT_NAME = f"{INTEGRATION_IDENTIFIER} - Async Action Example"
CONNECTOR_SCRIPT_NAME = "f{INTEGRATION_IDENTIFIER} - Simple Connector Example"

# Default Configuration Parameter Values
DEFAULT_API_ROOT = "https://api.vatcomply.com"
DEFAULT_VERIFY_SSL = True

# API Constants
ENDPOINTS = {
    "ping": "/rates",
    "get-base-rate": "/rates",
}

# Timeouts
REQUEST_TIMEOUT = 30
ASYNC_ACTION_TIMEOUT_THRESHOLD_SEC = 60


# Parameter Values
class DDLEnum(Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [item.value for item in cls]


class CurrenciesDDLEnum(DDLEnum):
    SELECT_ONE = "Select One"
    USD = "USD"
    EUR = "EUR"
    CAD = "CAD"


class TimeFrameDDLEnum(DDLEnum):
    TODAY = "Today"
    LAST_WEEK = "Last 7 Days"
    CUSTOM = "Custom"

    def to_start_date(self) -> datetime.date:
        match self:
            case TimeFrameDDLEnum.TODAY:
                return datetime.date.today()
            case TimeFrameDDLEnum.LAST_WEEK:
                return datetime.date.today() - datetime.timedelta(days=7)
            case _:
                raise ValueError(
                    f"Cannot convert object {self} to Date object",
                )


class SupportedEntitiesEnum(DDLEnum):
    ALL = "All Entities"
    IP = "IP"
    HASH = "Hash"
    USER = "User"

    def to_entity_type_enum_list(self) -> list[EntityTypesEnum]:
        match self:
            case SupportedEntitiesEnum.IP:
                return [EntityTypesEnum.ADDRESS]
            case SupportedEntitiesEnum.HASH:
                return [
                    EntityTypesEnum.FILE_HASH,
                    EntityTypesEnum.CHILD_HASH,
                    EntityTypesEnum.PARENT_HASH,
                ]
            case SupportedEntitiesEnum.USER:
                return [EntityTypesEnum.USER]
            case SupportedEntitiesEnum.ALL:
                return (
                    SupportedEntitiesEnum.IP.to_entity_type_enum_list()
                    + SupportedEntitiesEnum.HASH.to_entity_type_enum_list()
                    + SupportedEntitiesEnum.USER.to_entity_type_enum_list()
                )
            case _:
                raise ValueError("Unfamiliar Entity type")


class AlertSeverityEnum(DDLEnum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

    @property
    def severity(self) -> int:
        return ALERT_SEVERITY_MAP[self]


ALERT_SEVERITY_MAP: Mapping[AlertSeverityEnum, int] = {
    AlertSeverityEnum.CRITICAL: 100,
    AlertSeverityEnum.HIGH: 80,
    AlertSeverityEnum.MEDIUM: 60,
    AlertSeverityEnum.LOW: 40,
    AlertSeverityEnum.INFORMATIONAL: -1,
}
