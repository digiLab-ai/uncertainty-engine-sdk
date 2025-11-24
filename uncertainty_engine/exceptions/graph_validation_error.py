DEFAULT_GRAPH_FAILURE_MESSAGE = "Graph Validation Failed"


class GraphValidationError(Exception):
    """
    Raised when validating the graph fails.

    Args:
        validation_error: An optional high-level error message.
    """

    def __init__(
        self,
        validation_error: str = DEFAULT_GRAPH_FAILURE_MESSAGE,
    ):
        self.validation_error = validation_error
        """
        A high-level error message describing reason for validation
        failure.
        """

        super().__init__(self.validation_error)
