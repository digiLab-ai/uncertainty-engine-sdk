from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import Handle

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion, OldHandle


@typechecked
class Add(Node):
    """
    Add two numbers.

    Args:
        lhs: The left-hand side number.
        rhs: The right-hand side number.
        label: A human-readable label for the node. Defaults to None.
    """

    node_name: str = "demo.Add"

    def __init__(
        self,
        lhs: HandleUnion[float],
        rhs: HandleUnion[float],
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            lhs=OldHandle(lhs) if isinstance(lhs, Handle) else lhs,
            rhs=OldHandle(rhs) if isinstance(rhs, Handle) else rhs,
        )
