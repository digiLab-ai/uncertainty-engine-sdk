from uncertainty_engine_types import Handle

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.basic import Add


def test_add_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the `Add` node."""
    label = "Test Add"
    node = Add(
        lhs=mock_handle,
        rhs=2,
        label=label,
        client=mock_client,
    )

    assert node.node_name == "Add"
    assert node.lhs == mock_handle
    assert node.rhs == 2
    assert node.label == label
    assert node.client == mock_client
