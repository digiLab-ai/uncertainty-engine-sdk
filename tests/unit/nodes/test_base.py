from unittest.mock import MagicMock, patch
from warnings import catch_warnings

import pytest
from pytest import mark, raises
from typeguard import TypeCheckError
from uncertainty_engine_types import Handle, NodeInfo, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.client import Client
from uncertainty_engine.exceptions import NodeValidationError
from uncertainty_engine.nodes.base import Node


def test_node():
    """
    Verify result for arbitrary test node.
    """
    node = Node("test_node", a=1, b=2)
    assert node.node_name == "test_node"
    assert node.client is None
    assert node.node_info is None
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


def test_node_no_client_warnings():
    """
    Assert that when no `client` is given a warning is raised.
    """
    with catch_warnings(record=True) as warnings:
        # Patch validate (before creating `Node` instance)
        # We mock it to make sure no calls are made
        with patch.object(Node, "validate") as mock_validate:
            node = Node(node_name="test_node")

        assert node.client is None
        assert node.node_info is None

        # Assert warning only shows once
        assert len(warnings) == 1

        # Assert warning is correct
        assert (
            str(warnings[0].message)
            == "A `client` is required to get node info and perform validation."
        )

        # Assert `validate` is not called
        mock_validate.assert_not_called()


def test_node_with_client(default_node_info: NodeInfo):
    """
    Assert `Node` initialisation sets the correct attributes and calls
    `validate` when a `client` argument is present.
    """
    # Mock client
    test_client = MagicMock(spec=Client)
    test_client.get_node_info = MagicMock(return_value=default_node_info)

    # Patch validate (before creating `Node` instance)
    with patch.object(Node, "validate") as mock_validate:
        node = Node("test_node", client=test_client, a=1, b=2)

    assert node.node_name == "test_node"
    assert node.client == test_client
    assert node.node_info == default_node_info
    assert node.a == 1
    assert node.b == 2
    assert node.label is None
    assert node() == ("test_node", {"a": 1, "b": 2})

    # Assert `get_node_info` is called with correct args.
    test_client.get_node_info.assert_called_once_with("test_node")

    # Assert `validate` is called once
    mock_validate.assert_called_once()


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


def test_node_make_handle_with_node_info(add_node_info: NodeInfo):
    """
    Verify result for test node with `make_handle` method when
    `node_info` is available.
    """
    node = Node("TestAdd", label="test_label", lhs=1, rhs=2)
    node.node_info = add_node_info
    with catch_warnings(record=True) as warnings:
        assert node.make_handle("ans") == Handle("test_label.ans")
        assert len(warnings) == 0


@mark.parametrize("output_name", ["a", "output", "", "Answer"])
def test_node_make_handle_invalid_handle_error(
    add_node_info: NodeInfo, output_name: str
):
    """
    Verify result for test node with `make_handle` method and that
    correct error is raised when output name does not exist.
    """
    node = Node("TestAdd", label="test_label")
    node.node_info = add_node_info
    with pytest.raises(NodeValidationError) as excinfo:
        assert node.make_handle(output_name) == Handle(f"test_label.{output_name}")
        assert (
            str(excinfo.value)
            == f"Invalid output names: ['{output_name}']. Please make a handle using any of the following outputs instead: ['ans']."
        )


def test_add_tool_input(default_node_info: NodeInfo):
    """
    Verify that add_tool_input correctly adds a tool input to the node's metadata.
    """
    node = Node("test_node", label="test_node")
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
    node = Node("test_node", label="test_node")
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
    node = Node("test_node", label="test_node")
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
    node = Node("test_node", label="test_node")
    default_node_info.outputs = {
        "output1": NodeOutputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    with pytest.raises(KeyError, match="Output handle 'output2' does not exist"):
        node.add_tool_output("output2", default_node_info)


def test_validate_no_errors(
    default_node_info: NodeInfo,
):
    """
    Assert `validate` does not raise and return `None` when validators
    do not raise.
    """
    node = Node(node_name="test_node")
    node.node_info = default_node_info

    with patch(
        "uncertainty_engine.nodes.base.validate_required_inputs"
    ) as mock_validate_req, patch(
        "uncertainty_engine.nodes.base.validate_inputs_exist"
    ) as mock_validate_exist:

        mock_validate_req.return_value = None
        mock_validate_exist.return_value = None

        assert node.validate() is None


@pytest.mark.parametrize(
    "inputs_required,missing_inputs, expected_err",
    [
        (True, True, "err1\nerr2"),
        (True, False, "err1"),
        (False, True, "err2"),
    ],
)
def test_validate_errors(
    default_node_info: NodeInfo,
    inputs_required: bool,
    missing_inputs: bool,
    expected_err: str,
):
    """
    Assert `validate` raises a collection of all errors raised by
    validators.
    """
    node = Node(node_name="test_node")
    node.node_info = default_node_info

    with patch(
        "uncertainty_engine.nodes.base.validate_required_inputs"
    ) as mock_validate_req, patch(
        "uncertainty_engine.nodes.base.validate_inputs_exist"
    ) as mock_validate_exist:

        mock_validate_req.side_effect = (
            NodeValidationError("err1") if inputs_required else None
        )
        mock_validate_exist.side_effect = (
            NodeValidationError("err2") if missing_inputs else None
        )

        with raises(NodeValidationError, match=expected_err):
            node.validate()


def test_validate_raises_without_node_info():
    """
    Assert that `validate` raises a `ValueError` when `self.node_info`
    is `None`.
    """
    node = Node(node_name="test_node", a=1)

    with raises(ValueError, match="Node info is not available for validation."):
        node.validate()


def test_call_basic_functionality():
    """
    Verify that __call__ returns correct tuple with node name and filtered inputs.
    """
    node = Node("test_node", a=1, b=2, c="test")
    node_name, inputs = node()

    assert node_name == "test_node"
    assert inputs == {"a": 1, "b": 2, "c": "test"}


def test_call_excludes_internal_attributes(default_node_info: NodeInfo):
    """
    Verify that internal attributes are excluded from the input dictionary.
    """
    node = Node("test_node", label="test_label", a=1, b=2)
    default_node_info.inputs = {
        "input1": NodeInputInfo(
            type="int", label="test node", description="test node desc"
        )
    }

    node.add_tool_input("input1", default_node_info)

    node_name, inputs = node()

    assert node_name == "test_node"
    assert inputs == {"a": 1, "b": 2}
    assert "node_name" not in inputs
    assert "label" not in inputs
    assert "client" not in inputs
    assert "node_info" not in inputs
    assert "tool_metadata" not in inputs
