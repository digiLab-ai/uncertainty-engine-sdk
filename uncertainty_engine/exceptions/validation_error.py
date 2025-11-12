class ValidationError(Exception):
    """Raised when one or more node validation checks fail."""

    def __init__(self, errors: list[str] | str):
        if isinstance(errors, str):
            errors = [errors]
        self.errors = errors
        message = "\n".join(errors)
        super().__init__(message)
