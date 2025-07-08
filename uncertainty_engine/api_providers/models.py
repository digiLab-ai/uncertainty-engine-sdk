from typing import Any, Literal, Optional

from pydantic import BaseModel, Field
from uncertainty_engine_types import Graph, Handle

# TODO: Have workflow unified in types library

ValueRef = dict[str, Any]
HandleRef = dict[str, Handle]


class WorkflowInputs(BaseModel):
    graph: dict[str, Graph]
    inputs: ValueRef
    requested_output: dict[str, HandleRef]
    external_input_id: str = Field(default="_")


class WorkflowExecutable(BaseModel):
    node_id: Literal["Workflow"]
    inputs: WorkflowInputs


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
