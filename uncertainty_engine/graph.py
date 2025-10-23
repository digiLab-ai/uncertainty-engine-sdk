import inspect
from typing import Optional, Type, Union

from typeguard import typechecked
from uncertainty_engine_types import Handle

from uncertainty_engine.nodes.base import Node


@typechecked
class Graph:
    """
    Define a graph of nodes that can be executed by the Uncertainty Engine.

    Args:
        external_input_id: String identifier that refers to external inputs to the graph.

    Example:
        >>> graph = Graph()
        >>> graph.add_node(
        ...    node=Add(lhs=1, rhs=2),
        ...    label="add_1"
        ... )
        >>> graph.nodes
        {'nodes': {'add_1': {'type': 'Add',
        'inputs': {'lhs': {'node_name': '_', 'node_handle': 'add_1_lhs'},
        'rhs': {'node_name': '_', 'node_handle': 'add_1_rhs'}}}}}
    """

    def __init__(self, external_input_id: str = "_"):
        self.nodes = {"nodes": dict()}
        self.external_input_id = external_input_id
        self.external_input = dict()
        self.tool_metadata = {"inputs": {}, "outputs": {}}

    def add_node(
        self, node: Union[Node, Type[Node]], label: Optional[str] = None
    ) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.
            label: The label of the node. This must be unique. If not provided must be an attribute of the node.
                Defaults to None.
        """

        # add tool_metadata
        self._process_metadata(node)

        if isinstance(node, Node):
            if label is None and node.label is None:
                raise ValueError("Nodes must have a non-None label.")
            elif label is None:
                label = node.label

            node_input_dict = dict()
            for ki, vi in node.__dict__.items():
                if ki not in ["node_name", "label", "tool_metadata"]:
                    if isinstance(vi, Handle):
                        node_input_dict[ki] = vi.model_dump()
                    else:
                        node_input_dict[ki] = {
                            "node_name": self.external_input_id,
                            "node_handle": f"{label}_{ki}",
                        }
                        self.external_input[f"{label}_{ki}"] = vi

        else:
            if label is None:
                raise ValueError("Nodes must have a non-None label.")

            node_input_dict = {
                ki: None
                for ki in inspect.signature(node.__init__).parameters.keys()
                if ki not in ["self", "label"]
            }

        self.nodes["nodes"][label] = {"type": node.node_name, "inputs": node_input_dict}

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

    def _process_metadata(self, node: Union[Node, Type[Node]]) -> None:
        """
        Process and serialize metadata for a given node.

        This function extracts metadata from the `tool_metadata` attribute of
        the node, if it exists, and serializes the `tool_inputs` and
        `tool_outputs` into the `tool_metadata` dictionary of the graph.
        If the values in `tool_inputs` or `tool_outputs` have a `model_dump`
        method, it is used for serialization; otherwise, the raw value is stored.

        Args:
            node: The node whose metadata is to be processed.

        """

        if hasattr(node, "tool_metadata"):
            if "tool_inputs" in node.tool_metadata.keys():
                # ensure to serialize inputs
                self.tool_metadata["inputs"][node.label] = {
                    key: value.model_dump() if hasattr(value, "model_dump") else value
                    for key, value in node.tool_metadata["tool_inputs"].items()
                }

            if "tool_outputs" in node.tool_metadata.keys():
                # ensure to serialize outputs
                self.tool_metadata["outputs"][node.label] = {
                    key: value.model_dump() if hasattr(value, "model_dump") else value
                    for key, value in node.tool_metadata["tool_outputs"].items()
                }
