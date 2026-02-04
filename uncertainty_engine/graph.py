import inspect
from typing import Optional, Type, Union
from warnings import warn

from typeguard import typechecked
from uncertainty_engine_types import Handle, ToolMetadata

from uncertainty_engine.exceptions import GraphValidationError
from uncertainty_engine.nodes.base import Node


@typechecked
class Graph:
    """
    Define a graph of nodes that can be executed by the Uncertainty
    Engine.

    Args:
        external_input_id: String identifier that refers to external
            inputs to the graph.
        prevent_node_overwrite: If True, prevents adding nodes with
            duplicate labels. Defaults to False.

    Example:
        >>> graph = Graph()
        >>> graph.add_node(
        ...    node=Node(node_name="Add", lhs=1, rhs=2),
        ...    label="add_1"
        ... )
        >>> graph.nodes
        {'nodes': {'add_1': {'type': 'Add',
        'inputs': {'lhs': {'node_name': '_', 'node_handle': 'add_1_lhs'},
        'rhs': {'node_name': '_', 'node_handle': 'add_1_rhs'}}}}}
    """

    def __init__(
        self, external_input_id: str = "_", prevent_node_overwrite: bool | None = None
    ):
        self.nodes = {"nodes": dict()}
        self.external_input_id = external_input_id
        self.external_input = dict()
        self.tool_metadata: ToolMetadata = ToolMetadata()
        if prevent_node_overwrite is None:
            warn(
                "The default value of `prevent_node_overwrite` "
                "will change to `True` in a future release. "
                "Please set this argument explicitly to `False` "
                "to maintain the ability to overwrite nodes.",
                FutureWarning,
            )
            prevent_node_overwrite = False
        self.prevent_node_overwrite = prevent_node_overwrite

    def add_node(
        self, node: Union[Node, Type[Node]], label: Optional[str] = None
    ) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.
            label: The label of the node. This must be unique. If not provided must be an attribute of the node.
                Defaults to None.

        Example:
            >>> graph = Graph()
            >>> graph.add_node(
            ...    node=Node(node_name="Number", value=5),
            ...    label="number_1"
            ... )
            >>> graph.nodes
            {'nodes': {'number_1': {'type': 'Number',
            'inputs': {'value': {'node_name': '_',
            'node_handle': 'number_1_value'}}}}}
        """

        # Make sure we have a label to use
        if label is None and isinstance(node, Node):
            label = node.label
        if label is None:
            raise ValueError("Nodes must have a non-None label.")

        if self.prevent_node_overwrite:
            self.validate_label_is_unique(label)

        if isinstance(node, Node):
            node_input_dict = dict()

            # Calling the node will return a dictionary containing the
            # node inputs and their assigned value (which could be a
            # `Handle`), which is then remapped so that non-Handle values
            # are stored in the `self.external_input` dictionary.
            _, node_inputs = node()
            for ki, vi in node_inputs.items():
                if isinstance(vi, Handle):
                    node_input_dict[ki] = vi.model_dump()
                else:
                    node_input_dict[ki] = {
                        "node_name": self.external_input_id,
                        "node_handle": f"{label}_{ki}",
                    }
                    self.external_input[f"{label}_{ki}"] = vi

        else:
            node_input_dict = {
                ki: None
                for ki in inspect.signature(node.__init__).parameters.keys()
                if ki not in ["self", "label", "client"]
            }

        self.nodes["nodes"][label] = {"type": node.node_name, "inputs": node_input_dict}

        # add tool_metadata
        self._process_metadata(node)

    def add_nodes_from(self, nodes: list[Node]) -> None:
        """
        Add multiple nodes to the graph.

        Args:
            nodes: A list of nodes to add.
        """
        for node in nodes:
            self.add_node(node)

    def add_edge(
        self, source: str, source_key: str, target: str, target_key: str
    ) -> None:
        """
        Add an edge between two nodes in the graph.

        Args:
            source: The source node.
            source_key: The output key of the source node.
            target: The target node.
            target_key: The input key of the target node.

        Example:
            >>> graph = Graph()
            >>> graph.add_node(Node(node_name="Number", value=5, label="number_1"))
            >>> graph.add_node(Node(node_name="Add", lhs=0, rhs=0, label="add_1"))
            >>> graph.add_edge("number_1", "value", "add_1", "lhs")
            >>> print(graph.nodes)
            {'nodes': {'number_1': {'type': 'Number',
            'inputs': {'value': {'node_name': '_',
            'node_handle': 'number_1_value'}}},
            'add_1': {'type': 'Add', 'inputs': {'lhs': {'node_name': 'number_1',
            'node_handle': 'value'}, 'rhs': {'node_name': '_', 'node_handle': 'add_1_rhs'}}}}}
        """
        self.nodes["nodes"][target]["inputs"][target_key] = {
            "node_name": source,
            "node_handle": source_key,
        }

    def add_input(self, key: str, value) -> None:
        """
        Add an external input to the graph.

        Args:
            key: The key of the input.
            value: The value of the input.
        """
        self.external_input[key] = value

    def validate_label_is_unique(self, label: str) -> None:
        """
        Validate that a node label is unique within the graph.

        Args:
            label: The label to validate.

        Raises:
            GraphValidationError: If the label is not unique.
        """

        if label in self.nodes["nodes"]:
            raise GraphValidationError(f"Label '{label}' already used in the graph")

    def validate_tool_metadata(self) -> None:
        """
        Validate that tool metadata is complete (has both inputs and outputs).

        This should be called before saving/serializing the graph.

        Raises:
            ValueError: If tool metadata is partially defined (only inputs or only outputs)
        """
        if not self.tool_metadata.is_empty():
            self.tool_metadata.validate_complete()

    def _process_metadata(self, node: Union[Node, Type[Node]]) -> None:
        """
        Process metadata for a given node.

        This function extracts metadata from the `tool_metadata` attribute of
        the node, if it exists, and directly assigns the `tool_inputs` and
        `tool_outputs` into the `tool_metadata` dictionary of the graph.

        Args:
            node: The node whose metadata is to be processed.
        """

        if not hasattr(node, "tool_metadata") or not isinstance(node, Node):
            return

        node_metadata: ToolMetadata = node.tool_metadata

        # Merge inputs - update existing dict with node's inputs
        self.tool_metadata.inputs.update(node_metadata.inputs)

        # Merge outputs - update existing dict with node's outputs
        self.tool_metadata.outputs.update(node_metadata.outputs)
