from typing import Any
from unittest.mock import patch

from pytest import mark, raises
from uncertainty_engine_types import NodeElement, NodeInfo

from uncertainty_engine.exceptions import WorkflowValidationError
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


def test_workflow_validator_validate_node_inputs_no_errors(
    add_node_info: NodeInfo,
    node_info_list: list[NodeInfo],
    workflow_node_graph: dict[str, Any],
):
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
        validator._validate_node_inputs(test_node)

        mock_validate_req.assert_called_once_with(add_node_info, node_element.inputs)
        mock_validate_exist.assert_called_once_with(add_node_info, node_element.inputs)

    assert validator.node_errors == []
