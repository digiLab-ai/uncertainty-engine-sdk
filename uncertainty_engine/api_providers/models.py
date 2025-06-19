from typing import Optional

from pydantic import BaseModel


class WorkflowRecord(BaseModel):
    id: Optional[str] = None
    name: str
    owner_id: str
    created_at: Optional[str] = None
    versions: list[str] = []
