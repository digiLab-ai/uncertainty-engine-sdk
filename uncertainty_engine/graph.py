import inspect
from typing import Type, Union

from typeguard import typechecked

from uncertainty_engine.nodes.base import Node


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

    def add_node(self, node: Union[Node, Type[Node]], label: str) -> None:
        """
        Add a node to the graph.

        Args:
            node: The node to add.
            label: The label of the node. This must be unique.
        """
        if isinstance(node, Node):
            node_input_dict = dict()
            for ki, vi in node.__dict__.items():
                if ki != "node_name":
                    node_input_dict[ki] = (self.external_input_id, f"{label}_{ki}")
                    self.external_input[f"{label}_{ki}"] = vi

        else:
            node_input_dict = {
                ki: None
                for ki in inspect.signature(node.__init__).parameters.keys()
                if ki != "self"
            }

        self.nodes["nodes"][label] = {"type": node.node_name, "inputs": node_input_dict}

    def add_edge(
        self, source: str, target: str, source_key: str, target_key: str
    ) -> None:
        """
        Add an edge between two nodes in the graph.

        Args:
            source: The source node.
            target: The target node.
            source_key: The output key of the source node.
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
