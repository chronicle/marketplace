from __future__ import annotations

from typing import TYPE_CHECKING

import dataclasses

if TYPE_CHECKING:
    from TIPCommon.types import SingleJson
    from TIPCommon.base.interfaces.logger import ScriptLogger


@dataclasses.dataclass(slots=True)
class IntegrationParameters:
    api_root: str
    client_id: str
    client_secret: str
    verify_ssl: bool
    siemplify_logger: ScriptLogger


@dataclasses.dataclass(slots=True)
class BaseModel:
    raw_data: SingleJson

    def to_json(self) -> SingleJson:
        """Convert the model to a JSON serializable format."""
        return self.raw_data


@dataclasses.dataclass(slots=True)
class Issue(BaseModel):
    issue_id: str

    @classmethod
    def from_json(cls, json_data: SingleJson) -> Issue:
        """Create an Issue instance from JSON data."""
        return cls(raw_data=json_data, issue_id=json_data["id"])


@dataclasses.dataclass(slots=True)
class IssueComment(BaseModel):
    comment_id: str

    @classmethod
    def from_json(cls, json_data: SingleJson) -> IssueComment:
        """Create an IssueComment instance from JSON data."""
        return cls(raw_data=json_data, comment_id=json_data["id"])
