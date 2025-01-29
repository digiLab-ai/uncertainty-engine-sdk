import pytest

from uncertainty_engine.nodes.base import Node


def test_node():
    """
    Verify result for arbitrary test node.
    """
    node = Node("test_node", a=1, b=2)
    assert node.node_name == "test_node"
    assert node.a == 1
    assert node.b == 2
    assert node() == ("test_node", {"a": 1, "b": 2})


def test_node_no_inputs():
    """
    Verify result for test node with no inputs.
    """
    node = Node("test_node")
    assert node.node_name == "test_node"
    assert node() == ("test_node", {})


def test_node_name_type():
    """
    Verify error is raised if node name is not a string.
    """
    with pytest.raises(TypeError):
        Node(5)
