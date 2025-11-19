from pydantic import BaseModel


class NodeErrorInfo(BaseModel):
    """Describes an error related to a node and its input parameters."""

    node_id: str
    """The unique id (label) for the invalid node in the graph."""

    message: str
    """The specific error message."""


class NodeHandleErrorInfo(NodeErrorInfo):
    """Describes an error related to a node handle reference."""

    input_id: str
    """The id of the input which references the invalid handle."""


class RequestedOutputErrorInfo(BaseModel):
    """
    Describes an error related to a requested output handle reference.
    """

    requested_output_id: str
    """The unique id (label) for the invalid requested output."""

    message: str
    """The specific error message."""


class WorkflowValidationError(Exception):
    """
    Raised when validating an entire workflow fails.

    Args:
        validation_error: An optional high-level error message
            describing the reason for validation failure. Defaults to
            generic validation failure message.
        node_errors: An optional list of errors related to nodes and
            their input parameters.
        node_handle_errors: An optional list of errors related to
            node handle references.
        requested_output_errors: An optional list of errors related to
            requested output handle references.
    """

    def __init__(
        self,
        validation_error: str = "Workflow Validation Failed",
        node_errors: list[NodeErrorInfo] | None = None,
        node_handle_errors: list[NodeHandleErrorInfo] | None = None,
        requested_output_errors: list[RequestedOutputErrorInfo] | None = None,
    ):
        self.validation_error = validation_error
        """
        A high-level error message describing reason for validation
        failure.
        """

        self.node_errors = node_errors or []
        """Errors related to nodes and their input parameters."""

        self.node_handle_errors = node_handle_errors or []
        """Errors related to node handle references."""

        self.requested_output_errors = requested_output_errors or []
        """Errors related to requested output handle references."""

        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Returns a human-readable categorised summary of errors."""
        parts: list[str] = [self.validation_error]

        if self.node_errors:
            parts.append("")
            parts.append("Node Errors:")
            for err in self.node_errors:
                parts.append(f"  - {err.node_id}: {err.message}")

        if self.node_handle_errors:
            parts.append("")
            parts.append("Handle Errors:")
            for err in self.node_handle_errors:
                parts.append(f"  - {err.node_id} -> {err.input_id}: {err.message}")

        if self.requested_output_errors:
            parts.append("")
            parts.append("Requested Output Errors:")
            for err in self.requested_output_errors:
                parts.append(f"  - {err.requested_output_id}: {err.message}")

        return "\n".join(parts)
