from typing import Any
from unittest.mock import patch

from pytest import mark, raises
from uncertainty_engine_types import NodeElement, NodeInfo

from uncertainty_engine.exceptions import (
    NodeErrorInfo,
    NodeHandleErrorInfo,
    NodeValidationError,
    WorkflowValidationError,
)
from uncertainty_engine.workflow_validator import WorkflowValidator


def test_workflow_validator_init(
    node_info_list: list[NodeInfo],
    add_node_info: NodeInfo,
    display_node_info: NodeInfo,
    workflow_node_graph: dict[str, Any],
    workflow_node_inputs: dict[str, Any],
    workflow_node_requested_output: dict[str, Any],
):
    """Assert validator does not raise when workflow is correct."""
    validator = WorkflowValidator(
        node_info_list=node_info_list,
        graph=workflow_node_graph,
        inputs=workflow_node_inputs,
        requested_output=workflow_node_requested_output,
    )

    assert validator.node_infos == {
        "TestAdd": add_node_info,
        "TestDisplay": display_node_info,
    }
    assert validator.node_errors == []
    assert validator.node_handle_errors == []
    assert validator.requested_output_errors == []


@mark.parametrize(
    "invalid_graph, expected_error",
    [
        ({"invalid": "nodes"}, "Invalid workflow graph\n  - nodes: Field required"),
        (
            {"nodes": {"nodes": {}}},
            "Invalid workflow graph\n  - nodes -> nodes -> type: Field required",
        ),
        ({}, "Invalid workflow graph\n  - nodes: Field required"),
        (
            {
                "nodes": {
                    "Test Display": {
                        "inputs": {"value": 2},
                        "type": "TestDisplay",
                    },
                }
            },
            "Invalid workflow graph\n  - nodes -> Test Display -> inputs -> value: Input should be a valid dictionary or instance of Handle",
        ),
        (
            {
                "nodes": [
                    {"Display": {}},
                    {"First Add": {}},
                ]
            },
            "Invalid workflow graph\n  - nodes: Input should be a valid dictionary",
        ),  # type: ignore
        (
            {
                "nodes": {
                    "First Add": {
                        "inputs": [
                            {"lhs": {...}},
                            {"rhs": {...}},
                        ],
                        "type": 1,
                    }
                }
            },
            "Invalid workflow graph\n  - nodes -> First Add -> type: Input should be a valid string\n  - nodes -> First Add -> inputs: Input should be a valid dictionary",
        ),
    ],
)
def test_workflow_validator_init_value_error(
    node_info_list: list[NodeInfo], invalid_graph: dict[str, Any], expected_error: str
):
    """
    Assert validator fails to initialise when args cannot be
    instantiated as relevant pydantic types.
    """
    with raises(
        WorkflowValidationError,
        match=expected_error,
    ):
        WorkflowValidator(node_info_list, invalid_graph)


@mark.parametrize(
    "validation_errors",
    [
        ["missing required inputs", "inputs do not exist"],
        [None, "inputs do not exist"],
        ["missing required inputs", None],
        [None, None],
    ],
)
def test_workflow_validator_validate_node_inputs(
    add_node_info: NodeInfo,
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
    validation_errors: list[str | None],
):
    """
    Assert `_validate_node_inputs` stores input validation errors under
    `self.node_errors` with associated node id and error message.
    """
    validator = WorkflowValidator(
        node_info_list=node_info_list,
        graph=workflow_node_graph,
    )

    node_id = "Test Add"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    with patch(
        "uncertainty_engine.workflow_validator.validate_required_inputs"
    ) as mock_validate_req, patch(
        "uncertainty_engine.workflow_validator.validate_inputs_exist"
    ) as mock_validate_exist:
        mock_validate_req.side_effect = (
            NodeValidationError(validation_errors[0]) if validation_errors[0] else None
        )
        mock_validate_exist.side_effect = (
            NodeValidationError(validation_errors[1]) if validation_errors[1] else None
        )

        validator._validate_node_inputs(test_node)

        mock_validate_req.assert_called_once_with(add_node_info, node_element.inputs)
        mock_validate_exist.assert_called_once_with(add_node_info, node_element.inputs)

    expected_errors = [
        NodeErrorInfo(node_id="Test Add", message=msg)
        for msg in validation_errors
        if msg
    ]

    assert validator.node_errors == expected_errors


def test_workflow_validator_validate_node_inputs_node_type_error(
    workflow_node_graph: dict[str, Any],
):
    """
    Asserts `_validate_node_inputs` stores correct error message with
    associated node id if teh node type does not exist.
    """
    validator = WorkflowValidator(
        node_info_list=[],
        graph=workflow_node_graph,
    )

    node_id = "Test Add"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator._validate_node_inputs(test_node)

    assert validator.node_errors == [
        NodeErrorInfo(node_id="Test Add", message="The 'TestAdd' node does not exist.")
    ]


@mark.parametrize("node_id", ["Test Add", "Test Display"])
def test_validate_handles_no_errors(
    node_id: str,
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
    workflow_node_inputs: dict[str, Any],
):
    """Assert no errors are stored when handles are valid."""
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator = WorkflowValidator(
        node_info_list=node_info_list,
        graph=workflow_node_graph,
        inputs=workflow_node_inputs,
    )
    validator._validate_handles(test_node)
    assert validator.node_handle_errors == []


@mark.parametrize("inputs", [None, {}, {"invalid": "Test Add_lhs"}])
def test_validate_handles_input_error(
    inputs: dict[str, Any],
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
):
    """
    Assert correct errors are stored when handles are invalid input
    references.
    """
    node_id = "Test Add"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator = WorkflowValidator(
        node_info_list=node_info_list,
        graph=workflow_node_graph,
        inputs=inputs,
    )
    validator._validate_handles(test_node)
    assert validator.node_handle_errors == [
        NodeHandleErrorInfo(
            node_id=node_id,
            message="External input 'Test Add_lhs' does not exist.",
            input_id="lhs",
        ),
        NodeHandleErrorInfo(
            node_id=node_id,
            input_id="rhs",
            message="External input 'Test Add_rhs' does not exist.",
        ),
    ]


def test_validate_handles_not_in_graph(
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
):
    """
    Assert correct errors are stored when handles are invalid graph
    references.
    """
    node_id = "Test Display"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator = WorkflowValidator(
        node_info_list=node_info_list,
        graph={"nodes": {node_id: node_element.model_dump()}},
    )
    validator._validate_handles(test_node)

    assert validator.node_handle_errors == [
        NodeHandleErrorInfo(
            node_id=node_id,
            input_id="value",
            message="Node with label 'Test Add' is referenced but is not in graph.",
        ),
    ]


def test_validate_handles_node_does_not_exist(
    display_node_info: NodeInfo,
    workflow_node_graph: dict[str, Any],
):
    """
    Assert correct errors are stored when handle `node_name` does not
    references a node type that does not exist.
    """
    node_id = "Test Display"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator = WorkflowValidator(
        node_info_list=[display_node_info],
        graph=workflow_node_graph,
    )
    validator._validate_handles(test_node)

    assert validator.node_handle_errors == [
        NodeHandleErrorInfo(
            node_id=node_id,
            input_id="value",
            message="The 'TestAdd' node does not exist.",
        ),
    ]


def test_validate_handles_outputs_invalid(
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
):
    """
    Assert correct errors are stored when handle `node_handle` does not
    exist on node.
    """
    node_id = "Test Display"
    node_element = NodeElement(**workflow_node_graph["nodes"][node_id])
    test_node = (node_id, node_element)

    validator = WorkflowValidator(
        node_info_list=node_info_list, graph=workflow_node_graph
    )
    with patch(
        "uncertainty_engine.workflow_validator.validate_outputs_exist"
    ) as mock_validate_outputs:
        mock_validate_outputs.side_effect = NodeValidationError("output does not exist")
        validator._validate_handles(test_node)

    assert validator.node_handle_errors == [
        NodeHandleErrorInfo(
            node_id="Test Display",
            input_id="value",
            message="output does not exist",
        )
    ]
