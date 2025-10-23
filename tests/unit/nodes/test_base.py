import pytest
from typeguard import TypeCheckError
from uncertainty_engine_types import Handle, NodeInfo, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.nodes.base import Node


@pytest.fixture
def default_node_info():
    """
    Provide a default NodeInfo object for tests.
    """
    return NodeInfo(
        id="default_id",
        label="default_label",
        category="default_category",
        description="default_description",
        long_description="default_long_description",
        image_name="default_image",
        cost=0,
        version_base_image=1,
        version_node=1,
        inputs={},
        outputs={},
    )


def test_node():
    """
    Verify result for arbitrary test node.
    """
    node = Node("test_node", a=1, b=2)
    assert node.node_name == "test_node"
    assert node.a == 1
    assert node.b == 2
    assert node.label is None
    assert node() == ("test_node", {"tool_metadata": {}, "a": 1, "b": 2})


def test_node_no_inputs():
    """
    Verify result for test node with no inputs.
    """
    node = Node("test_node")
    assert node.node_name == "test_node"
    assert node() == ("test_node", {"tool_metadata": {}})


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


def test_add_tool_input(default_node_info: NodeInfo):
    """
    Verify that add_tool_input correctly adds a tool input to the node's metadata.
    """
    node = Node("test_node")
    default_node_info.inputs = {
        "input1": NodeInputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    node.add_tool_input("input1", default_node_info)

    assert "tool_inputs" in node.tool_metadata
    assert "input1" in node.tool_metadata["tool_inputs"]
    assert node.tool_metadata["tool_inputs"]["input1"]["type"] == "int"
    assert node.tool_metadata["tool_inputs"]["input1"]["label"] == "test node"
    assert (
        node.tool_metadata["tool_inputs"]["input1"]["description"] == "test node desc"
    )


def test_add_tool_input_missing_handle(default_node_info: NodeInfo):
    """
    Verify that add_tool_input raises a KeyError if the handle does not exist in the inputs.
    """
    node = Node("test_node")
    default_node_info.inputs = {
        "input1": NodeInputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    with pytest.raises(KeyError, match="Input handle 'input2' does not exist"):
        node.add_tool_input("input2", default_node_info)


def test_add_tool_output(default_node_info: NodeInfo):
    """
    Verify that add_tool_output correctly adds a tool output to the node's metadata.
    """
    node = Node("test_node")
    default_node_info.outputs = {
        "output1": NodeOutputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    node.add_tool_output("output1", default_node_info)

    assert "tool_outputs" in node.tool_metadata
    assert "output1" in node.tool_metadata["tool_outputs"]
    assert node.tool_metadata["tool_outputs"]["output1"]["type"] == "int"
    assert node.tool_metadata["tool_outputs"]["output1"]["label"] == "test node"
    assert (
        node.tool_metadata["tool_outputs"]["output1"]["description"] == "test node desc"
    )


def test_add_tool_output_missing_handle(default_node_info: NodeInfo):
    """
    Verify that add_tool_output raises a KeyError if the handle does not exist in the outputs.
    """
    node = Node("test_node")
    default_node_info.outputs = {
        "output1": NodeOutputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    with pytest.raises(KeyError, match="Output handle 'output2' does not exist"):
        node.add_tool_output("output2", default_node_info)
