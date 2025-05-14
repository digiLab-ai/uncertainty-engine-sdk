from uncertainty_engine.auth_service import AuthService


class ApiProviderBase:
    """Base class for all API clients with automatic token refresh"""

    def __init__(self, deployment: str, auth_service: AuthService):
        self.deployment = deployment
        self.auth_service = auth_service
