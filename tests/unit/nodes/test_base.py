import pytest
from uncertainty_engine_types import Handle

from uncertainty_engine.nodes.base import Node
from typeguard import TypeCheckError


def test_node():
    """
    Verify result for arbitrary test node.
    """
    node = Node("test_node", a=1, b=2)
    assert node.node_name == "test_node"
    assert node.a == 1
    assert node.b == 2
    assert node.label is None
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
    with pytest.raises(TypeCheckError):
        Node(5)


def test_node_make_handle():
    """
    Verify result for test node with make_handle method.
    """
    node = Node("test_node", label="test_label", a=1, b=2)
    assert node.make_handle("output") == Handle("test_label.output")


def test_node_make_handle_no_label():
    """
    Verify error is raised if node has no label.
    """
    node = Node("test_node", a=1, b=2)
    with pytest.raises(ValueError):
        node.make_handle("output")
