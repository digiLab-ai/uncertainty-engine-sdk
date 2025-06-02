class IncompleteCredentials(Exception):
    """
    Raised when the user's credentials are incomplete.

    Args:
        env_var: The name of the environment variable that's incomplete.
    """

    def __init__(self, env_var: str) -> None:
        super().__init__(f"The {env_var} environment variable must be set.")
