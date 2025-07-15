from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, field_validator
from uncertainty_engine_resource_client.models import ProjectRecordOutput

from uncertainty_engine.api_providers.constants import DATETIME_STRING_FORMAT


class WorkflowExecutable(BaseModel):
    node_id: Literal["Workflow"]
    inputs: dict[str, Any]


class WorkflowRecord(BaseModel):
    id: Optional[str] = None
    name: str
    owner_id: str
    created_at: Optional[str] = None
    versions: list[str] = []


class WorkflowVersion(BaseModel):
    id: Optional[str] = None
    workflow_id: Optional[str] = None
    name: str
    owner_id: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProjectRecord(ProjectRecordOutput):
    model_config = ConfigDict(
        from_attributes=True,
    )

    @field_validator("created_at", "updated_at", mode="after")
    def parse_datetime(cls, value: datetime | None) -> str | None:
        """Convert datetime object to ISO string."""
        if not value:
            return None
        return value.strftime(DATETIME_STRING_FORMAT)
