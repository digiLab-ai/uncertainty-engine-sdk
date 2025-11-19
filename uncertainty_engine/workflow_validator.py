from typing import Any

from pydantic import ValidationError
from typeguard import typechecked
from uncertainty_engine_types import Graph as WorkflowNodeGraph
from uncertainty_engine_types import NodeInfo

from uncertainty_engine.exceptions import (
    NodeErrorInfo,
    NodeHandleErrorInfo,
    RequestedOutputErrorInfo,
    WorkflowValidationError,
)
from uncertainty_engine.utils import format_pydantic_error


class WorkflowValidator:
    """
    Takes all workflow node inputs along with a list of all available
    node info and is used to perform full workflow validation.

    Args:
        nodes_list: List of node info dictionaries as fetched from
    """

    @typechecked
    def __init__(
        self,
        node_info_list: list[NodeInfo],
        graph: dict[str, Any],
        inputs: dict[str, Any] | None = None,
        requested_output: dict[str, Any] | None = None,
        external_input_id: str = "_",
    ):
        self.node_infos = {node_info.id: node_info for node_info in node_info_list}
        self.inputs = inputs
        self.external_input_id = external_input_id
        self.requested_output = requested_output

        # Validate graph shape using Pydantic.
        # Will be unable to validate workflow if graph is incorrect
        # shape so this error is raised immediately.
        try:
            self.graph = WorkflowNodeGraph(**graph)
        except ValidationError as e:
            raise WorkflowValidationError(
                f"Invalid workflow graph:\n" + format_pydantic_error(e)
            )

        self.node_errors: list[NodeErrorInfo] = []
        self.node_handle_errors: list[NodeHandleErrorInfo] = []
        self.requested_output_errors: list[RequestedOutputErrorInfo] = []
