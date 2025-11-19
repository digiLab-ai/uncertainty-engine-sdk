from uncertainty_engine.exceptions import (
    NodeErrorInfo,
    NodeHandleErrorInfo,
    RequestedOutputErrorInfo,
    WorkflowValidationError,
)

DEFAULT_VALIDATION_MESSAGE = "Workflow Validation Failed\n\n"


def test_workflow_validation_error_node_errors():
    """Assert node errors are formatted correctly."""
    node_errors = [
        NodeErrorInfo(node_id="node1", message="Missing required input"),
        NodeErrorInfo(node_id="node2", message="Input does not exist"),
    ]

    err = WorkflowValidationError(node_errors=node_errors)
    received = str(err)
    expected = (
        DEFAULT_VALIDATION_MESSAGE + "Node Errors:\n"
        "  - node1: Missing required input\n"
        "  - node2: Input does not exist"
    )
    assert expected == received


def test_workflow_validation_error_handle_errors():
    """Assert node handle errors are formatted correctly."""
    handle_errors = [
        NodeHandleErrorInfo(
            node_id="node",
            input_id="input1",
            message="Handle reference invalid",
        ),
        NodeHandleErrorInfo(
            node_id="node",
            input_id="input2",
            message="Handle reference invalid",
        ),
    ]

    err = WorkflowValidationError(node_handle_errors=handle_errors)
    received = str(err)
    expected = (
        DEFAULT_VALIDATION_MESSAGE + "Handle Errors:\n"
        "  - node -> input1: Handle reference invalid\n"
        "  - node -> input2: Handle reference invalid"
    )
    assert expected == received


def test_workflow_validation_error_requested_output_errors():
    """Assert requested output errors are formatted correctly."""
    req_errors = [
        RequestedOutputErrorInfo(
            requested_output_id="node",
            message="Requested output not found",
        )
    ]

    err = WorkflowValidationError(requested_output_errors=req_errors)
    received = str(err)
    expected = (
        DEFAULT_VALIDATION_MESSAGE
        + "Requested Output Errors:\n  - node: Requested output not found"
    )
    assert expected == received


def test_workflow_validation_error_all_errors():
    """Assert a combination of all errors are formatted correctly."""
    node_errors = [
        NodeErrorInfo(node_id="node1", message="Invalid node input"),
    ]
    handle_errors = [
        NodeHandleErrorInfo(
            node_id="node2",
            input_id="input",
            message="Invalid handle",
        )
    ]
    requested_errors = [
        RequestedOutputErrorInfo(
            requested_output_id="req_output",
            message="Invalid requested output",
        )
    ]

    err = WorkflowValidationError(
        node_errors=node_errors,
        node_handle_errors=handle_errors,
        requested_output_errors=requested_errors,
    )
    received = str(err)
    expected = (
        DEFAULT_VALIDATION_MESSAGE + "Node Errors:\n"
        "  - node1: Invalid node input\n"
        "\n"
        "Handle Errors:\n"
        "  - node2 -> input: Invalid handle\n"
        "\n"
        "Requested Output Errors:\n"
        "  - req_output: Invalid requested output"
    )
    assert expected == received
