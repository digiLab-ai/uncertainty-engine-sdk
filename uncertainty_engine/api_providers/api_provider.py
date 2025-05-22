from functools import wraps
from typing import Any, Callable, NoReturn, TypeVar

from uncertainty_engine_resource_client.exceptions import UnauthorizedException

from uncertainty_engine.auth_service import AuthService

# Define a type variable for return values
T = TypeVar("T")

MAX_RETRIES = 1


class ApiProviderBase:
    """Base class for all API clients with automatic token refresh"""

    def __init__(self, deployment: str, auth_service: AuthService):
        self.deployment = deployment
        self.auth_service = auth_service

    @classmethod
    def with_auth_refresh(cls, func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(self: ApiProviderBase, *args: Any, **kwargs: Any) -> T:
            try:
                return func(self, *args, **kwargs)
            except UnauthorizedException:
                # Refresh token
                self.auth_service.refresh()
                self.update_api_authentication()
                # Retry the operation with refreshed token
                return func(self, *args, **kwargs)
            except Exception:
                raise

        return wrapper

    def update_api_authentication(self) -> NoReturn:
        """
        All API providers that wish to use token refreshing must implement this method.
        This method should update the authorization header in the api client.
        """
        raise NotImplementedError("Subclasses must implement update_api_authentication")
