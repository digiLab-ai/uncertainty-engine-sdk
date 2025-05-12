from uncertainty_engine.auth_service import AuthService


class ApiProviderBase:
    """Base class for all API clients with automatic token refresh"""

    def __init__(self, base_url: str, auth_service: AuthService):
        self.base_url = base_url
        self.auth_service = auth_service
