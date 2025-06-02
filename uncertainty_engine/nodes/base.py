from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import Handle


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
