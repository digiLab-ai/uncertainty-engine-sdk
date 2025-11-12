from typing import Any

from uncertainty_engine_types import NodeInfo
from uncertainty_engine.exceptions import ValidationError


def validate_required_inputs(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    # Check required inputs
    required_inputs = [name for name, info in node_info.inputs.items() if info.required]
    missing_inputs = list(set(required_inputs) - set(node_inputs))

    if len(missing_inputs) > 0:
        raise ValidationError(f"Missing required inputs: {missing_inputs}")


def validate_inputs_exist(node_info: NodeInfo, node_inputs: dict[str, Any]) -> None:
    # Check input names
    invalid_input_names = list(set(node_inputs) - set(node_info.inputs))

    if len(invalid_input_names) > 0:
        raise ValidationError(f"Invalid input names: {invalid_input_names}")
