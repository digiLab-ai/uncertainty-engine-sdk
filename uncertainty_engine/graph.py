import inspect
from typing import Optional, Type, Union

from typeguard import typechecked

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import OldHandle


@typechecked
class Graph:
    """
    Define a graph of nodes that can be executed by the Uncertainty Engine.

    Args:
        external_input_id: String identifier that refers to external inputs to the graph.
    """

    def __init__(self, external_input_id: str = "_"):
        self.nodes = {"nodes": dict()}
        self.external_input_id = external_input_id
        self.external_input = dict()

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
        if isinstance(node, Node):
            if label is None and node.label is None:
                raise ValueError("Nodes must have a non-None label.")
            elif label is None:
                label = node.label

            node_input_dict = dict()
            for ki, vi in node.__dict__.items():
                if ki not in ["node_name", "label"]:
                    if isinstance(vi, OldHandle):
                        node_input_dict[ki] = vi()
                    else:
                        node_input_dict[ki] = (self.external_input_id, f"{label}_{ki}")
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
        self.nodes["nodes"][target]["inputs"][target_key] = (source, source_key)

    def add_input(self, key: str, value) -> None:
        """
        Add an external input to the graph.

        Args:
            key: The key of the input.
            value: The value of the input.
        """
        self.external_input[key] = value
