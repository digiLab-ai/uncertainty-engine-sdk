class GraphValidationError(Exception):
    """
    Raised when validating the graph fails.

    Args:
        validation_error: A high-level error message describing reason
            for validation failure.
    """

    def __init__(
        self,
        validation_error: str,
    ):
        self.validation_error = validation_error
        """
        A high-level error message describing reason for validation
        failure.
        """

        super().__init__(self.validation_error)
