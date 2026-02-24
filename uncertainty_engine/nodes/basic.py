from typeguard import typechecked

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.protocols import Client
from uncertainty_engine.utils import HandleUnion


@typechecked
class Add(Node):
    """
    Add two numbers.

    Args:
        lhs: The left-hand side number.
        rhs: The right-hand side number.
        label: A human-readable label for the node. Defaults to None.
        client: An (optional) instance of the client being used. This is
            required for performing validation.
    """

    node_name: str = "Add"
    """The node ID."""

    lhs: HandleUnion[float]
    """The left-hand side number."""

    rhs: HandleUnion[float]
    """The right-hand side number."""

    def __init__(
        self,
        lhs: HandleUnion[float],
        rhs: HandleUnion[float],
        label: str | None = None,
        client: Client | None = None,
    ):
        super().__init__(
            node_name=self.node_name,
            version="0.2.0",
            label=label,
            client=client,
            lhs=lhs,
            rhs=rhs,
        )
