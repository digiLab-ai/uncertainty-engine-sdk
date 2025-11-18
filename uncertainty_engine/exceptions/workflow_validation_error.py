from pydantic import BaseModel


class NodeErrorInfo(BaseModel):
    node_id: str
    message: str


class NodeHandleErrorInfo(NodeErrorInfo):
    input_id: str


class RequestedOutputErrorInfo(BaseModel):
    requested_output_id: str
    message: str


class WorkflowValidationError(Exception):
    """
    Raised when validating an entire workflow fails.

    Contains structured details for:
      - node_errors
      - node_handle_errors
      - requested_output_errors
    """

    def __init__(
        self,
        node_errors: list[NodeErrorInfo] | None = None,
        node_handle_errors: list[NodeHandleErrorInfo] | None = None,
        requested_output_errors: list[RequestedOutputErrorInfo] | None = None,
    ):
        self.node_errors = node_errors or []
        self.node_handle_errors = node_handle_errors or []
        self.requested_output_errors = requested_output_errors or []

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Returns a human-readable summary of errors."""
        parts: list[str] = []

        if self.node_errors:
            parts.append("Node Errors:")
            for err in self.node_errors:
                parts.append(f"  - [{err.node_id}] {err.message}")

        if self.node_handle_errors:
            # add empty line if previous section exists
            if parts:
                parts.append("")
            parts.append("Handle Errors:")
            for err in self.node_handle_errors:
                parts.append(f"  - [{err.node_id}:{err.input_id}] {err.message}")

        if self.requested_output_errors:
            if parts:
                parts.append("")
            parts.append("Requested Output Errors:")
            for err in self.requested_output_errors:
                parts.append(f"  - [{err.requested_output_id}] {err.message}")

        return "\n".join(parts)
