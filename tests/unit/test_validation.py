from re import escape
from typing import Any

from pytest import mark, raises
from uncertainty_engine_types import NodeInfo, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.exceptions import NodeValidationError
from uncertainty_engine.validation import (
    validate_inputs_exist,
    validate_required_inputs,
    validate_outputs_exist,
)


@mark.parametrize(
    "node_inputs,node_info_inputs",
    [
        (
            {"a": 1, "x": 99},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
        ),
        (
            {"y": 10},
            {
                "a": NodeInputInfo(type="", label="", description="", required=False),
            },
        ),
    ],
)
def test_validate_required_inputs(
    default_node_info: NodeInfo,
    node_inputs: dict[str, Any],
    node_info_inputs: dict[str, NodeInputInfo],
):
    """
    Assert `validate_required_inputs` returns `None` with no errors
    raised when inputs are correct.
    """
    default_node_info.inputs = node_info_inputs
    assert validate_required_inputs(default_node_info, node_inputs) is None


@mark.parametrize(
    "node_inputs,node_info_inputs,expected_error",
    [
        # Missing required input
        (
            {"b": 1},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
            "Missing required inputs: ['a']",
        ),
        # Missing required input included as value but not as key
        (
            {"b": "a"},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=True),
                "c": NodeInputInfo(type="", label="", description="", required=True),
            },
            "Missing required inputs: ['a', 'c']",
        ),
        (
            {"y": 10},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
            },
            "Missing required inputs: ['a']",
        ),
    ],
)
def test_validate_required_inputs_errors(
    default_node_info: NodeInfo,
    node_inputs: dict[str, Any],
    node_info_inputs: dict[str, NodeInputInfo],
    expected_error: str,
):
    """
    Assert `validate_required_inputs` raises the correct errors given
    different incorrect input combinations.
    """
    default_node_info.inputs = node_info_inputs
    with raises(NodeValidationError, match=escape(expected_error)):
        validate_required_inputs(default_node_info, node_inputs)


@mark.parametrize(
    "node_inputs,node_info_inputs",
    [
        (
            {"a": 1, "b": 99},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
        ),
        (
            {"a": 10},
            {
                "a": NodeInputInfo(type="", label="", description="", required=False),
            },
        ),
        (
            {"b": 99},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
        ),
    ],
)
def test_validate_inputs_exist(
    default_node_info: NodeInfo,
    node_inputs: dict[str, Any],
    node_info_inputs: dict[str, NodeInputInfo],
):
    """
    Assert `validate_inputs_exist` returns `None` with no errors
    raised when inputs are correct.
    """
    default_node_info.inputs = node_info_inputs
    assert validate_inputs_exist(default_node_info, node_inputs) is None


@mark.parametrize(
    "node_inputs,node_info_inputs,expected_error",
    [
        (
            {"a": 1, "x": 99},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
                "b": NodeInputInfo(type="", label="", description="", required=False),
            },
            "Invalid input names: ['x']",
        ),
        (
            {"y": 10},
            {
                "a": NodeInputInfo(type="", label="", description="", required=True),
            },
            "Invalid input names: ['y']",
        ),
    ],
)
def test_validate_inputs_exist_errors(
    default_node_info: NodeInfo,
    node_inputs: dict[str, Any],
    node_info_inputs: dict[str, NodeInputInfo],
    expected_error: str,
):
    """
    Assert `validate_inputs_exist` raises the correct errors given
    different incorrect input combinations.
    """
    default_node_info.inputs = node_info_inputs
    with raises(NodeValidationError, match=escape(expected_error)):
        validate_inputs_exist(default_node_info, node_inputs)


@mark.parametrize(
    "node_outputs,node_info_outputs",
    [
        (
            ["a", "b"],
            {
                "a": NodeOutputInfo(type="", label="", description=""),
                "b": NodeOutputInfo(type="", label="", description=""),
            },
        ),
        (
            "a",
            {
                "a": NodeOutputInfo(type="", label="", description=""),
            },
        ),
        (
            ["b", "b"],
            {
                "a": NodeOutputInfo(type="", label="", description=""),
                "b": NodeOutputInfo(type="", label="", description=""),
            },
        ),
    ],
)
def test_validate_outputs_exist(
    default_node_info: NodeInfo,
    node_outputs: str | list[str],
    node_info_outputs: dict[str, NodeOutputInfo],
):
    """
    Assert `validate_outputs_exist` returns `None` with no errors
    raised when outputs are correct.
    """
    default_node_info.outputs = node_info_outputs
    assert validate_outputs_exist(default_node_info, node_outputs) is None


@mark.parametrize(
    "node_outputs,node_info_outputs,expected_error",
    [
        (
            ["a", "x"],
            {
                "a": NodeOutputInfo(type="", label="", description=""),
                "b": NodeOutputInfo(type="", label="", description=""),
            },
            "Invalid output names: ['x']",
        ),
        (
            "y",
            {
                "a": NodeOutputInfo(type="", label="", description=""),
            },
            "Invalid output names: ['y']",
        ),
        (
            ["y", "y", "a", "x"],
            {
                "a": NodeOutputInfo(type="", label="", description=""),
                "yx": NodeOutputInfo(type="", label="", description=""),
            },
            "Invalid output names: ['y', 'y', 'x']",
        ),
    ],
)
def test_validate_outputs_exist_errors(
    default_node_info: NodeInfo,
    node_outputs: str | list[str],
    node_info_outputs: dict[str, NodeOutputInfo],
    expected_error: str,
):
    """
    Assert `validate_outputs_exist` raises the correct errors given
    different incorrect output combinations.
    """
    default_node_info.outputs = node_info_outputs
    with raises(NodeValidationError, match=escape(expected_error)):
        validate_outputs_exist(default_node_info, node_outputs)
