from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import Handle, NodeInfo, NodeInputInfo, NodeOutputInfo


@typechecked
class Node:
    """
    A generic representation of a node in the Uncertainty Engine.

    Args:
        node_name: The name of the node.
        label: A human-readable label for the node. Defaults to None.
        **kwargs: Arbitrary keyword arguments representing the input parameters of the node.

    Example:
        >>> add_node = Node(
        ...     node_name="Add",
        ...     lhs=1,
        ...     rhs=2,
        ... )
        >>> add_node()
        ('Add', {'lhs': 1, 'rhs': 2})
    """

    def __init__(self, node_name: str, label: Optional[str] = None, **kwargs):
        self.node_name = node_name
        self.label = label
        self.tool_metadata = {}
        for key, value in kwargs.items():
            setattr(self, key, value)

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
            if key not in ["node_name", "label"]
        }
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

        return Handle(f"{self.label}.{output_name}")

    def add_tool_input(self, handle_name: str, node_info: NodeInfo) -> None:
        """
        Mark an input on a node as to be used as a tool input

        Args:
            handle_name: The name of the handle (input) to mark as a tool input
            node_info: The NodeInfo of the node

        Raises:
            KeyError: If the handle_name does not exist on the inputs of the node


        Example:
        >>> add_node = Node(
        ...     node_name="Add",
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

        self.tool_metadata["tool_inputs"][handle_name] = node_input

    def add_tool_output(self, handle_name: str, node_info: NodeInfo) -> None:
        """
        Mark an output on a node as to be used as a tool output

        Args:
            handle_name: The name of the handle (output) to mark as a tool output
            node_info: The NodeInfo of the node

        Raises:
            KeyError: If the handle_name does not exist on the outputs of the node


        Example:
        >>> add_node = Node(
        ...     node_name="Add",
        ...     lhs=1,
        ...     rhs=2,
        ... )
        >>> add_node_info = client.get_node_info("Add")
        >>> add_node.add_tool_input("ans", add_node_info)
        """

        if handle_name not in node_info.outputs:
            raise KeyError(
                f"Input handle '{handle_name}' does not exist on outputs: {node_info.outputs}"
            )

        node_output: NodeOutputInfo = node_info.outputs[handle_name]

        if "tool_outputs" not in self.tool_metadata:
            self.tool_metadata["tool_outputs"] = {}

        self.tool_metadata["tool_outputs"][handle_name] = node_output
