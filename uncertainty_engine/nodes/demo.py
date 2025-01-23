from typeguard import typechecked

from uncertainty_engine.nodes.base import Node


@typechecked
class Add(Node):
    """
    Add two numbers.

    Args:
        a: The first number.
        b: The second number.
    """

    def __init__(self, a: float, b: float):
        super().__init__(node_name="math.Add", a=a, b=b)
