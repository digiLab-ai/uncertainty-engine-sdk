from functools import wraps
from typing import Any, Callable, TypeVar

from uncertainty_engine_resource_client.exceptions import UnauthorizedException

from uncertainty_engine.auth_service import AuthService

# Define a type variable for return values
T = TypeVar("T")

MAX_RETRIES = 1


class ApiProviderBase:
    """Base class for all API clients with automatic token refresh"""

    def __init__(self, deployment: str, auth_service: AuthService):
        self.deployment = deployment.rstrip("/")
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

    def update_api_authentication(self) -> None:
        """
        All API providers that wish to use token refreshing must implement this method.
        This method should update the authorization header in the api client.
        """
        raise NotImplementedError("Subclasses must implement update_api_authentication")

    def get_id_by_name(
        self,
        list_func: Callable[[], list[T]],
        name: str,
        resource_type: str = "item",
        name_field: str = "name",
        id_field: str = "id",
    ) -> str:
        """
        Find a resource ID by searching for a matching name in a list of resources.

        This is a generic utility method that can work with any resource type that has
        name and ID fields. It calls the provided listing function to get all resources,
        then searches for one with the specified name.

        Args:
            list_func: A callable that returns a list of resources (takes no arguments)
            name: The name to search for
            resource_type: Human-readable name of the resource type (for error messages) (default: "")
            name_field: The attribute name to check for the name match (default: "name")
            id_field: The attribute name to extract the ID from (default: "id")

        Returns:
            str: The ID of the resource with the matching name

        Raises:
            ValueError: If no resource is found with the specified name

        Example:
            # Find a resource ID by name
            user_id = self.get_id_by_name(
                list_func=self.resources.list_resource(),
                name="resource_name",
                resource_type="resource"
            )
        """
        items = list_func()
        for item in items:
            if getattr(item, name_field) == name:
                return getattr(item, id_field)
        raise ValueError(f"No {resource_type} found with name: {name}")
