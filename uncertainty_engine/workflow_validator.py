from typing import Any

from uncertainty_engine_types import Graph as NodesGraph
from uncertainty_engine_types import Handle, NodeElement, NodeInfo

from uncertainty_engine.exceptions import (
    NodeErrorInfo,
    NodeHandleErrorInfo,
    NodeValidationError,
    RequestedOutputErrorInfo,
    WorkflowValidationError,
)
from uncertainty_engine.validation import (
    validate_inputs_exist,
    validate_outputs_exist,
    validate_required_inputs,
)


class WorkflowValidator:
    def __init__(
        self,
        nodes_list: list[dict[str, Any]],
        graph: dict[str, Any],
        inputs: dict[str, Any] | None = None,
        requested_output: dict[str, Any] | None = None,
        external_input_id: str = "_",
    ):
        # TODO: Currently some attributes are converted to use stricter
        # type from types library. Once `Graph` and `Workflow` class are
        # updated to use these types, this conversion can be removed.
        try:
            self.nodes_lookup = {node["id"]: NodeInfo(**node) for node in nodes_list}
            self.graph = NodesGraph(**graph)
            self.inputs = inputs
            self.requested_output = (
                {key: Handle(**value) for key, value in requested_output.items()}
                if requested_output
                else None
            )
            self.external_input_id = external_input_id
        except Exception as e:
            raise ValueError(f"Unable to perform graph validation: {str(e)}.")

        self.node_errors: list[NodeErrorInfo] = []
        self.node_handle_errors: list[NodeHandleErrorInfo] = []
        self.requested_output_errors: list[RequestedOutputErrorInfo] = []

    def validate(self):
        for node in self.graph.nodes.items():
            self._validate_node_inputs(node)
            self._validate_handles(node)

        if self.requested_output:
            self._validate_requested_output(self.requested_output)

        if self.node_errors or self.node_handle_errors or self.requested_output_errors:
            raise WorkflowValidationError(
                node_errors=self.node_errors,
                node_handle_errors=self.node_handle_errors,
                requested_output_errors=self.requested_output_errors,
            )

    def _validate_node_inputs(self, node: tuple[str, NodeElement]):
        node_id, node_element = node

        # Check node exists and get node_info
        node_info = self.nodes_lookup.get(node_id)
        if node_info is None:
            raise NodeValidationError(f"The '{node_id}' does not exist.")

        for validator in (validate_required_inputs, validate_inputs_exist):
            try:
                validator(node_info, node_element.inputs)
            except NodeValidationError as e:
                self.node_errors.append(NodeErrorInfo(node_id=node_id, message=str(e)))

    def _get_handle_error_message(self, handle: Handle) -> str | None:
        # Check handle is a valid external input reference
        if handle.node_name == self.external_input_id:
            if (not self.inputs) or (handle.node_handle not in self.inputs):
                return f"External input '{handle.node_handle}' does not exist."

        # Check handle `node_name` is in graph
        handle_node = self.graph.nodes.get(handle.node_name)
        if handle_node is None:
            return f"Node with label '{handle.node_name}' is referenced to but is not in graph."

        # Check node exists
        node_info = self.nodes_lookup.get(handle_node.type)
        if node_info is None:
            return f"The '{handle_node.type}' node does not exist."

        # Check outputs exist
        try:
            validate_outputs_exist(node_info, handle.node_handle)
        except NodeValidationError as e:
            return str(e)

    def _validate_handles(self, node: tuple[str, NodeElement]):
        node_id, node_element = node
        for input_id, handle in node_element.inputs.items():
            message = self._get_handle_error_message(handle)
            if message:
                self.node_handle_errors.append(
                    NodeHandleErrorInfo(
                        node_id=node_id, input_id=input_id, message=message
                    )
                )

    def _validate_requested_output(self, requested_output: dict[str, Handle]):
        for output_id, handle in requested_output.items():
            message = self._get_handle_error_message(handle)
            if message:
                self.requested_output_errors.append(
                    RequestedOutputErrorInfo(
                        requested_output_id=output_id, message=message
                    )
                )
