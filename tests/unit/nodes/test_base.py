from typing import Any
from unittest.mock import MagicMock, patch
from warnings import catch_warnings, simplefilter

import pytest
from pytest import raises
from typeguard import TypeCheckError
from uncertainty_engine_types import Handle, NodeInfo, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.client import Client
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
        # Set so python always shows warning
        simplefilter("always")

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


def test_node_make_handle_no_node_info_warning():
    """
    Verify result for test node with make_handle method and that correct
    warnings are shown when node info is not available.
    """
    node = Node("TestAdd", label="test_label")
    with catch_warnings(record=True) as warnings:
        # Set so python always shows warning
        simplefilter("always")

        # Assert correct warning is shown when no node info available
        assert node.make_handle("answer") == Handle("test_label.answer")
        assert len(warnings) == 1
        assert (
            str(warnings[0].message)
            == "Skipping validation as node info is not available."
        )


def test_node_make_handle_invalid_handle_warning(add_node_info: NodeInfo):
    """
    Verify result for test node with make_handle method and that correct
    warnings are shown when node info is not available.
    """
    node = Node("TestAdd", label="test_label")
    node.node_info = add_node_info
    with catch_warnings(record=True) as warnings:
        # Set so python always shows warning
        simplefilter("always")

        # Assert correct warning is shown when no node info available
        assert node.make_handle("answer") == Handle("test_label.answer")
        assert len(warnings) == 1
        assert (
            str(warnings[0].message)
            == f"Output 'answer' does not exist please use one of the following: ['ans']"
        )


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


@pytest.mark.parametrize(
    "node_inputs,node_info_inputs,expected_warnings",
    [
        # Missing required input
        (
            {"b": 1},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
            ["Missing required inputs: ['a']"],
        ),
        # Missing required input included as value but not as key
        (
            {"b": "a"},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=True),
            },
            ["Missing required inputs: ['a']"],
        ),
        # Invalid input name
        (
            {"a": 1, "x": 99},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
            },
            ["Invalid input names: ['x']"],
        ),
        # Both missing and invalid inputs
        (
            {"y": 10},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
            },
            ["Missing required inputs: ['a']", "Invalid input names: ['y']"],
        ),
        # No warnings
        (
            {"a": 1},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
            },
            [],
        ),
        # No warnings when no required inputs
        (
            {},
            {
                "a": NodeInputInfo(type="", label="", description="", required=False),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
            [],
        ),
    ],
)
def test_validate_warnings(
    default_node_info: NodeInfo,
    node_inputs: dict[str, Any],
    node_info_inputs: dict[str, NodeInputInfo],
    expected_warnings: list[str],
):
    """
    Assert `validate` displays the correct warnings given different input
    combinations.
    """
    default_node_info.inputs = node_info_inputs
    test_client = MagicMock(spec=Client)
    test_client.get_node_info = MagicMock(return_value=default_node_info)
    node = Node(node_name="test_node", client=test_client, **node_inputs)

    with catch_warnings(record=True) as warnings:
        # Set so python always shows warning
        simplefilter("always")

        # Run validate and collect warning messages
        node.validate()
        warning_messages = [str(w.message) for w in warnings]

        # Check that each expected warning matches a received warning
        for expected in expected_warnings:
            assert any(expected in msg for msg in warning_messages), (
                f"Expected warning containing '{expected}' not found in received warnings:\n"
                f"{warning_messages}"
            )

        # Ensure no unexpected warnings
        assert len(warning_messages) == len(expected_warnings)


def test_validate_raises_without_node_info():
    """
    Assert that `validate` raises a `ValueError` when `self.node_info`
    is `None`.
    """
    node = Node(node_name="test_node", a=1)

    with raises(ValueError, match="Node info is not available for validation."):
        node.validate()
