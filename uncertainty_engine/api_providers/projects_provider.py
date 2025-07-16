from typing import Optional

from pydantic import ValidationError
from uncertainty_engine_resource_client.api import AccountRecordsApi, ProjectRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import ProjectRecordOutput

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.api_providers.constants import DEFAULT_RESOURCE_DEPLOYMENT
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
    ) -> list[ProjectRecordOutput]:
        """
        List all projects in your account.

        Returns:
            A list of project records, each with:
                - id: The unique identifier of the project
                - name: The friendly name of the project
                - owner_id: The account ID of the user who owns the project
                - description: Description of the project
                - members: Dictionary containing members of the project and their access level
                           (will be empty if the owner is the only member)
                - created_at: The creation date of the project (ISO 8601 format)
                - updated_at: The date of the last update to the project (ISO 8601 format)
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError("Authentication required before listing projects.")

        try:
            response = self.accounts_client.get_account_record_projects(
                self.account_id
            ).project_records
            return [ProjectRecordOutput.model_validate(record) for record in response]
        except ApiException as e:
            raise Exception(f"Failed to fetch project records: {format_api_error(e)}")
        except (ValidationError, Exception) as e:
            raise Exception(f"Error listing project records: {str(e)}")
