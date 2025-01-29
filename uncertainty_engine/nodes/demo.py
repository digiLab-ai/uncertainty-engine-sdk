from typeguard import typechecked

from uncertainty_engine.nodes.base import Node


@typechecked
class Add(Node):
    """
    Add two numbers.

    Args:
        lhs: The left-hand side number.
        rhs: The right-hand side number.
    """

    node_name: str = "demo.Add"

    def __init__(self, lhs: float, rhs: float):
        super().__init__(node_name=self.node_name, lhs=lhs, rhs=rhs)
