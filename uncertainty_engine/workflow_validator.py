from typing import Any

from pydantic import ValidationError
from typeguard import typechecked
from uncertainty_engine_types import Graph as WorkflowNodeGraph
from uncertainty_engine_types import NodeElement, NodeInfo

from uncertainty_engine.exceptions import (
    NodeErrorInfo,
    NodeHandleErrorInfo,
    NodeValidationError,
    RequestedOutputErrorInfo,
    WorkflowValidationError,
)
from uncertainty_engine.utils import format_pydantic_error
from uncertainty_engine.validation import (
    validate_inputs_exist,
    validate_required_inputs,
)


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
                "Invalid workflow graph\n" + format_pydantic_error(e)
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

    def _validate_node_inputs(self, node: tuple[str, NodeElement]) -> None:
        """
        Performs the following validation checks on an individual node
        and its input parameters:

            - Checks the node type exists
            - Checks the assigned inputs exist on that node type
            - Checks all required inputs have been assigned a value

        If any of these check fail the unique node id (label) and error
        message are stored in `self.node_errors` to be raised once
        validation finishes.

        Args:
            node: A tuple containing the node key (its unique id in the
                graph) and value (the assigned inputs and node type).
        """
        node_id, node_element = node

        # Check node exists and get relevant node info. If this check
        # fails the method will store the error and return as it will be
        # unable to perform input validation without the node info.
        node_info = self.node_infos.get(node_element.type)
        if node_info is None:
            self.node_errors.append(
                NodeErrorInfo(
                    node_id=node_id,
                    message=f"The '{node_element.type}' node does not exist.",
                )
            )
            return

        for validator in (validate_required_inputs, validate_inputs_exist):
            try:
                validator(node_info, node_element.inputs)
            except NodeValidationError as e:
                self.node_errors.append(NodeErrorInfo(node_id=node_id, message=str(e)))
