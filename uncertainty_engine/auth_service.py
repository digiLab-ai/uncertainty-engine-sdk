class AuthService:
    """Authentication service that manages tokens and provides them to API clients"""

    def __init__(self):
        self.account_id = None

    def authenticate(self, account_id: str) -> None:
        """Set authentication credentials"""
        self.account_id = account_id

    @property
    def is_authenticated(self) -> bool:
        """Check if authentication has been performed"""
        return self.account_id is not None
