from typing import Any

from uncertainty_engine_types import NodeInfo

from uncertainty_engine.exceptions import NodeValidationError


def validate_required_inputs(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    """
    Validates that all required inputs (as listed in the `node_info`)
    are included in the `node_inputs`.

    Args:
        node_info: A `NodeInfo` object used to validate the node inputs
            against.
        node_inputs: A dictionary containing the node inputs.

    Raises:
        `NodeValidationError`: If there are 1 or more missing required
            inputs. A list of the missing inputs is returned as part of
            the error message.
    """
    missing_inputs = [
        name
        for name, info in node_info.inputs.items()
        if info.required and name not in node_inputs
    ]

    if missing_inputs:
        raise NodeValidationError(f"Missing required inputs: {missing_inputs}")


def validate_inputs_exist(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    """
    Validates that all input names referenced in the `node_inputs` are
    existing input names (as defined by the `node_info`).

    Args:
        node_info: A `NodeInfo` object used to validate the node inputs
            against.
        node_inputs: A dictionary containing the node inputs.

    Raises:
        `NodeValidationError`: If there are 1 or more invalid input names.
            A list of the invalid input names is returned as part of the
            error message.
    """
    invalid_input_names = [
        name for name in node_inputs if (name not in node_info.inputs)
    ]

    if invalid_input_names:
        raise NodeValidationError(f"Invalid input names: {invalid_input_names}")


def validate_outputs_exist(node_info: NodeInfo, node_outputs: list[str]):
    """
    Validates that all output names referenced in the `node_outputs` are
    existing output names (as defined by the `node_info`).

    Args:
        node_info: A `NodeInfo` object used to validate the node outputs
            against.
        node_outputs: A list containing the node output names.

    Raises:
        `NodeValidationError`: If there are 1 or more invalid output
            names. A list of the invalid output names is returned as
            part of the error message.
    """
    invalid_output_names = [
        name for name in node_outputs if (name not in node_info.outputs)
    ]

    if invalid_output_names:
        raise NodeValidationError(f"Invalid output names: {invalid_output_names}.")
