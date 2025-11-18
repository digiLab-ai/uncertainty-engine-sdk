from uncertainty_engine.exceptions import (
    WorkflowValidationError,
    NodeErrorInfo,
    NodeHandleErrorInfo,
    RequestedOutputErrorInfo,
)
from uncertainty_engine_types import Handle


def test_workflow_validation_error_node_errors():
    """Assert node errors are formatted correctly."""
    node_errors = [
        NodeErrorInfo(node_id="node1", message="Missing required input"),
        NodeErrorInfo(node_id="node2", message="Input does not exist"),
    ]

    err = WorkflowValidationError(node_errors=node_errors)
    message = str(err)

    assert "Node Errors:" in message
    assert "  - [node1] Missing required input" in message
    assert "  - [node2] Input does not exist" in message


def test_workflow_validation_error_handle_errors():
    """Assert node handle errors are formatted correctly."""
    handle = Handle(node_name="X", node_handle="out1")

    handle_errors = [
        NodeHandleErrorInfo(
            node_id="X",
            handle=handle,
            message="Handle reference invalid",
        )
    ]

    err = WorkflowValidationError(node_handle_errors=handle_errors)
    message = str(err)

    assert "Handle Errors:" in message
    expected_dump = str(handle.model_dump())
    assert f"[X:{expected_dump}] Handle reference invalid" in message


def test_workflow_validation_error_requested_output_errors():
    """Assert requested output errors are formatted correctly."""
    req_errors = [
        RequestedOutputErrorInfo(
            requested_output_id="Z",
            message="Requested output not found",
        )
    ]

    err = WorkflowValidationError(requested_output_errors=req_errors)
    message = str(err)

    assert "Requested Output Errors:" in message
    assert "  - [Z] Requested output not found" in message


def test_workflow_validation_error_all_errors():
    """Assert a combination of all errors are formatted correctly."""
    node_errors = [
        NodeErrorInfo(node_id="A", message="Node invalid"),
    ]
    handle = Handle(node_name="B", node_handle="out1")
    handle_errors = [
        NodeHandleErrorInfo(
            node_id="B",
            handle=handle,
            message="Bad handle",
        )
    ]
    requested_errors = [
        RequestedOutputErrorInfo(
            requested_output_id="C",
            message="Invalid requested output",
        )
    ]

    err = WorkflowValidationError(
        node_errors=node_errors,
        node_handle_errors=handle_errors,
        requested_output_errors=requested_errors,
    )
    message = str(err)

    # Order matters
    assert message.index("Node Errors:") < message.index("Handle Errors:")
    assert message.index("Handle Errors:") < message.index("Requested Output Errors:")

    # Verify all details appear
    assert "[A] Node invalid" in message
    assert "[B" in message and "Bad handle" in message
    assert "[C] Invalid requested output" in message
