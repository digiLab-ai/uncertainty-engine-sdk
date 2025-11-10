from typing import Any, TypedDict
from warnings import warn

from typeguard import typechecked
from uncertainty_engine_types import Handle, NodeInfo, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.protocols import Client


class ToolMetadata(TypedDict, total=False):
    tool_inputs: dict[str, dict[str, Any]]
    tool_outputs: dict[str, dict[str, Any]]


@typechecked
class Node:
    """
    A generic representation of a node in the Uncertainty Engine.

    Args:
        node_name: The name of the node.
        label: A human-readable label for the node. Defaults to None.
        client: An (optional) instance of the client being used. This is
            required for performing validation.
        **kwargs: Arbitrary keyword arguments representing the input
            parameters of the node.

    Example:
        >>> client = Client()
        >>> add_node = Node(
        ...     node_name="Add",
        ...     lhs=1,
        ...     rhs=2,
        ...     client=client,
        ... )
        >>> add_node()
        ('Add', {'lhs': 1, 'rhs': 2})
    """

    def __init__(
        self,
        node_name: str,
        label: str | None = None,
        client: Client | None = None,
        **kwargs: Any,
    ):
        self.node_name = node_name
        """The name of the node."""

        self.label = label
        """A human-readable label for the node."""

        self.client = client
        """The Uncertainty Engine client."""

        self.node_info = client.get_node_info(self.node_name) if client else None
        """The node information. This includes the input parameters."""

        self.tool_metadata: ToolMetadata = {}
        """The node input and output handles to be used as tools."""

        for key, value in kwargs.items():
            setattr(self, key, value)

        if not client:
            warn(
                "A `client` is required to get node info and perform validation.",
                stacklevel=2,
            )
            return

        self.validate()

    def __call__(self) -> tuple[str, dict]:
        """
        Make the node callable. Simply creates a dictionary of the input parameters that can
        be passed to the Uncertainty Engine.

        Returns:
            A tuple containing the name of the node and the input parameters.
        """
        input = {
            key: getattr(self, key)
            for key in self.__dict__
            # NOTE: Currently any attribute names that are not input
            # parameters should be added here.
            if key not in ["node_name", "label", "client", "node_info"]
        }

        if "tool_metadata" in input and not input["tool_metadata"]:
            del input["tool_metadata"]

        return self.node_name, input

    def make_handle(self, output_name: str) -> Handle:
        """
        Make a handle for the output of the node.

        Args:
            output_name: The name of the output.

        Returns:
            A string handle for the output.
        """
        if self.label is None:
            raise ValueError("Nodes must have a label to make a handle.")

        handle = Handle(f"{self.label}.{output_name}")

        if not self.node_info:
            warn("Skipping validation as node info is not available.", stacklevel=2)
            return handle

        available_outputs = list(self.node_info.outputs)
        if output_name not in available_outputs:
            raise ValueError(
                f"Output '{output_name}' does not exist please use one of the following: {available_outputs}"
            )
        return handle

    def add_tool_input(self, handle_name: str, node_info: NodeInfo) -> None:
        """
        Mark an input on a node as to be used as a tool input

        Args:
            handle_name: The name of the handle (input) to mark as a tool input
            node_info: The NodeInfo of the node

        Raises:
            KeyError: If the handle_name does not exist on the inputs of the node


        Example:
        >>> add_node = Add(
        ...     label="Add node",
        ...     lhs=1,
        ...     rhs=2,
        ... )
        >>> add_node_info = client.get_node_info("Add")
        >>> add_node.add_tool_input("lhs", add_node_info)
        """

        if handle_name not in node_info.inputs:
            raise KeyError(
                f"Input handle '{handle_name}' does not exist on inputs: {node_info.inputs}"
            )

        node_input: NodeInputInfo = node_info.inputs[handle_name]

        if "tool_inputs" not in self.tool_metadata:
            self.tool_metadata["tool_inputs"] = {}

        self.tool_metadata["tool_inputs"][handle_name] = node_input.model_dump()

    def add_tool_output(self, handle_name: str, node_info: NodeInfo) -> None:
        """
        Mark an output on a node as to be used as a tool output

        Args:
            handle_name: The name of the handle (output) to mark as a tool output
            node_info: The NodeInfo of the node

        Raises:
            KeyError: If the handle_name does not exist on the outputs of the node


        Example:
        >>> add_node = Add(
        ...     label="Add node",
        ...     lhs=1,
        ...     rhs=2,
        ... )
        >>> add_node_info = client.get_node_info("Add")
        >>> add_node.add_tool_output("ans", add_node_info)
        """

        if handle_name not in node_info.outputs:
            raise KeyError(
                f"Output handle '{handle_name}' does not exist on outputs: {node_info.outputs}"
            )

        node_output: NodeOutputInfo = node_info.outputs[handle_name]

        if "tool_outputs" not in self.tool_metadata:
            self.tool_metadata["tool_outputs"] = {}

        self.tool_metadata["tool_outputs"][handle_name] = node_output.model_dump()

    def validate(self) -> None:
        """
        Validates the node parameters are correct according to the
        `node_info`. The following checks are made:

        - Check all required inputs are assigned a value or handle.
        - Check all the given input names exist in the node info.

        A warning is displayed to the user if either of these checks fail.

        Raises:
            `ValueError` if `self.node_info` is `None`.
        """
        if not self.node_info:
            raise ValueError("Node info is not available for validation.")

        # Get current node inputs
        _, node_input_dict = self()

        # Check required inputs
        required_inputs = [
            name for name, info in self.node_info.inputs.items() if info.required
        ]
        missing_inputs = list(set(required_inputs) - set(node_input_dict))

        if len(missing_inputs) > 0:
            warn(f"Missing required inputs: {missing_inputs}", stacklevel=2)

        # Check input names
        invalid_input_names = list(set(node_input_dict) - set(self.node_info.inputs))

        if len(invalid_input_names) > 0:
            warn(f"Invalid input names: {invalid_input_names}", stacklevel=2)
