from pydantic import BaseModel, field_validator
from uncertainty_engine_types import NodeInputInfo, NodeOutputInfo

NodeId = str
HandleLabel = str


# Graph-level metadata (aggregated from all nodes)
class ToolMetadata(BaseModel):
    """Metadata for tool inputs/outputs organized by node"""

    inputs: dict[NodeId, dict[HandleLabel, NodeInputInfo]] = {}
    outputs: dict[NodeId, dict[HandleLabel, NodeOutputInfo]] = {}

    def is_empty(self) -> bool:
        """Check if the metadata is completely empty"""
        return not self.inputs and not self.outputs

    def has_partial_data(self) -> bool:
        """Check if only inputs or only outputs are defined"""
        return bool(self.inputs) != bool(self.outputs)

    def validate_complete(self) -> None:
        """
        Validate that tool metadata is complete (has both inputs and outputs).

        Raises:
            ValueError: If metadata has only inputs or only outputs
        """
        if self.has_partial_data():
            raise ValueError(
                "Tool metadata must have both inputs AND outputs defined. "
                f"Currently has: inputs={'yes' if self.inputs else 'no'}, "
                f"outputs={'yes' if self.outputs else 'no'}"
            )
