from typing import Any, Optional

from uncertainty_engine_resource_client.api import AccountRecordsApi, ProjectRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import GetAccountRecordProjectsResponse

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.api_providers.constants import (
    DATETIME_STRING_FORMAT,
    DEFAULT_RESOURCE_DEPLOYMENT,
)
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.utils import format_api_error


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

    @ApiProviderBase.with_auth_refresh
    def list_projects(
        self,
    ) -> GetAccountRecordProjectsResponse:
        """
        List all projects in your account.

        Args:
            account_id: Your account's unique identifier

        Returns:
            A list of project records, each with: # TODO: replace the below
                - id: The unique identifier of the workflow
                - name: The friendly name of the workflow
                - owner_id: The ID of the user who owns the workflow
                - created_at: The creation date of the workflow in ISO 8601 format
                - versions: A list of version IDs associated with the workflow
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError("Authentication required before listing projects.")

        try:
            return self.accounts_client.get_account_record_projects(self.account_id)
        except ApiException as e:
            raise Exception(f"Error reading project records: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error reading project records: {str(e)}")
