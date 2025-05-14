from functools import wraps
from typing import Any, Callable, TypeVar

from uncertainty_engine_resource_client.exceptions import UnauthorizedException

from uncertainty_engine.auth_service import AuthService

# Define a type variable for return values
T = TypeVar("T")


class ApiProviderBase:
    """Base class for all API clients with automatic token refresh"""

    def __init__(self, deployment: str, auth_service: AuthService):
        self.deployment = deployment
        self.auth_service = auth_service

    def with_auth_refresh(
        cls, func: Callable[..., T], max_retries: int = 1
    ) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self, *args: Any, **kwargs: Any) -> T:
            retries = 0
            while retries <= max_retries:
                try:
                    return func(self, *args, **kwargs)
                except UnauthorizedException:
                    if retries >= max_retries:
                        raise
                    self.auth_service.refresh()
                    self._update_auth_headers()
                    retries += 1
            return func(self, *args, **kwargs)  # One final attempt

        return wrapper

    def _update_auth_headers(self):
        """
        All API providers that wish to use token refreshing must implement this method.
        This method should update the authorization header in the api client.
        """
        raise NotImplementedError("Subclasses must implement _update_auth_headers")
