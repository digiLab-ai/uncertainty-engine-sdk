from typing import Optional

from uncertainty_engine_resource_client.api import AccountRecordsApi, ProjectRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.api_providers.constants import (
    DEFAULT_RESOURCE_DEPLOYMENT,
)

from uncertainty_engine.auth_service import AuthService


class ProjectsProvider(ApiProviderBase):
    """
    Client for managing projects in the Uncertainty Engine platform.

    This client makes it easy to manage your Uncertainty Engine projects.
    Before using this client, you'll need to have authenticated using your account ID.
    """

    def __init__(
        self, auth_service: AuthService, deployment: str = DEFAULT_RESOURCE_DEPLOYMENT
    ):
        """
        Create an instance of a ProjectsProvider.

        Args:
            deployment: The URL of the resource service. You typically won't need
                        to change this unless instructed by support.
            auth_service: Handles your authentication.
        """
        super().__init__(deployment, auth_service)

        # Initialize the generated API client
        self.client = ApiClient(configuration=Configuration(host=deployment))
        # NOTE: The accounts client is currently required for GET projects endpoint
        self.accounts_client = AccountRecordsApi(self.client)
        self.projects_client = ProjectRecordsApi(self.client)

        # Update auth headers of the API client (only if authenticated)
        self.update_api_authentication()

    def update_api_authentication(self) -> None:  # type: ignore
        """Update API client with current auth headers"""
        if self.auth_service.is_authenticated:
            auth_header = self.auth_service.get_auth_header()
            self.client.default_headers.update(auth_header)

            # Update the API instances with the new header
            self.accounts_client.api_client.default_headers.update(auth_header)
            self.projects_client.api_client.default_headers.update(auth_header)

    @property
    def account_id(self) -> Optional[str]:
        """
        Get the current account ID from the auth provider

        Returns:
            The account ID if authenticated, otherwise None.
        """
        return self.auth_service.account_id
