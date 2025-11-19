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
    nodes and their info and is used to perform full workflow
    validation.

    Args:
        node_info_list: List of `NodeInfo` objects for each of the available
            nodes.
        graph: Workflow node input graph.
        inputs: Workflow node external inputs. Defaults to `None`.
        requested_output: Workflow node requested output. Defaults to
            `None`.
        external_input_id: Workflow node external input id. Defaults to
            "_" (same as workflow node).

    Raises:
        WorkflowValidationError: If workflow validation fails. Error
            message will contain details of failure.
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
        """
        A dictionary containing all available node infos to validate
        nodes against.
        """

        # Validate graph shape using Pydantic. This is required to
        # perform full graph validation so `WorkflowValidationError` is
        # raised immediately on failure.
        try:
            self.graph = WorkflowNodeGraph(**graph)
            """The graph of nodes to execute."""

        except ValidationError as e:
            raise WorkflowValidationError(
                "Invalid workflow graph:\n" + format_pydantic_error(e)
            )

        self.inputs = inputs
        """The external inputs to the workflow."""

        self.external_input_id = external_input_id
        """
        String identifier that refers to external inputs to the graph.
        """

        self.requested_output = requested_output
        """
        The requested output from the workflow.
        """

        # Categories of errors to be collected and raised once
        # validation is finished.
        self.node_errors: list[NodeErrorInfo] = []
        """Errors related to nodes and their input parameters."""

        self.node_handle_errors: list[NodeHandleErrorInfo] = []
        """Errors related to node handle references."""

        self.requested_output_errors: list[RequestedOutputErrorInfo] = []
        """Errors related to requested output handle references."""
