class NodeValidationError(Exception):
    """
    Raised when one or more node validation checks fail.

    Args:
        errors: Either a single or list of multiple string error
            messages.
    """

    def __init__(self, errors: list[str] | str):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors
        super().__init__("\n".join(errors))
