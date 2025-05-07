class AuthProvider:
    """Authentication state management"""

    def __init__(self):
        self.account_id = None

    def authenticate(self, account_id: str) -> None:
        """
        Set authentication credentials

        Args:
            account_id : The account ID to authenticate with.
        """
        self.account_id = account_id

    @property
    def is_authenticated(self) -> bool:
        """Check if authentication has been performed"""
        return self.account_id is not None
