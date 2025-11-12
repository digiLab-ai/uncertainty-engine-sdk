from typing import Any

from uncertainty_engine_types import NodeInfo
from uncertainty_engine.exceptions import ValidationError


def validate_required_inputs(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    """
    Validates that all required inputs (as listed in the `node_info`)
    are included in the `node_inputs`.

    Raises:
        `ValidationError`: If there are 1 or more missing required inputs.
            A list of the missing inputs is returned as part of the
            error message.
    """
    required_inputs = [name for name, info in node_info.inputs.items() if info.required]
    missing_inputs = list(set(required_inputs) - set(node_inputs))

    if len(missing_inputs) > 0:
        raise ValidationError(f"Missing required inputs: {missing_inputs}")


def validate_inputs_exist(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    """
    Validates that all input names referenced in the `node_inputs` are
    existing input names (as defined by the `node_info`).

    Raises:
        `ValidationError`: If there are 1 or more invalid input names.
            A list of the invalid input names is returned as part of the
            error message.
    """
    invalid_input_names = list(set(node_inputs) - set(node_info.inputs))

    if len(invalid_input_names) > 0:
        raise ValidationError(f"Invalid input names: {invalid_input_names}")
