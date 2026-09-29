from typing import Any


def node_info_dict(node_id: str, version: str | int = "latest") -> dict[str, Any]:
    """
    Build a `NodeInfo` response body for a two-input node.

    Args:
        node_id: The ID of the node.
        version: The node's version.

    Returns:
        A `NodeInfo` shaped dictionary.
    """
    return {
        "id": node_id,
        "label": node_id,
        "category": "test_category",
        "description": "A test node",
        "long_description": "A long description for the test node.",
        "image_name": "test_image.png",
        "cost": 0,
        "inputs": {
            "lhs": {"type": "float", "label": "LHS", "description": "Left"},
            "rhs": {"type": "float", "label": "RHS", "description": "Right"},
        },
        "outputs": {
            "ans": {"type": "float", "label": "Answer", "description": "Result"},
        },
        "version_base_image": 1,
        "version_node": version,
    }
