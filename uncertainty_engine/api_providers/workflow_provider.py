from typing import Optional

from uncertainty_engine_resource_client.api import ProjectRecordsApi, WorkflowsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostWorkflowRecordRequest,
    PostWorkflowVersionRequest,
    UpdateWorkflowVersionRequest,
    WorkflowRecordInput,
    WorkflowVersionRecordInput,
    WorkflowVersionRecordOutput,
)

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.nodes.workflow import Workflow
from uncertainty_engine.utils import format_api_error

DEFAULT_RESOURCE_DEPLOYMENT = "http://localhost:8001/api"


class WorkflowsProvider(ApiProviderBase):
    """
    Client for managing workflows in the Uncertainty Engine platform.

    This client makes it easy to save and load workflows stored in your
    Uncertainty Engine projects. Use this client when you need to:

    - Save workflows to your projects
    - Load workflows from your projects

    Before using this client, you'll need a project ID and appropriate access rights.
    """

    def __init__(
        self, auth_service: AuthService, deployment: str = DEFAULT_RESOURCE_DEPLOYMENT
    ):
        """
        Create an instance of a WorkflowsProvider.

        Args:
            deployment: The URL of the resource service. You typically won't need
                        to change this unless instructed by support.
            auth_service: Handles your authentication.
        """
        super().__init__(deployment, auth_service)

        # Initialize the generated API client
        self.client = ApiClient(configuration=Configuration(host=deployment))
        self.projects_client = ProjectRecordsApi(self.client)
        self.workflows_client = WorkflowsApi(self.client)

        # Update auth headers of the API client (only if authenticated)
        self.update_api_authentication()

    def update_api_authentication(self):
        """Update API client with current auth headers"""
        if self.auth_service.is_authenticated:

            auth_header = self.auth_service.get_auth_header()

            self.client.default_headers.update(auth_header)

            # Update the API instances with the new header
            self.projects_client.api_client.default_headers.update(auth_header)
            self.workflows_client.api_client.default_headers.update(auth_header)

        # Explicitly raise an exception to match the NoReturn type
        raise RuntimeError("update_api_authentication should not return normally.")

    @property
    def account_id(self) -> Optional[str]:
        """
        Get the current account ID from the auth provider

        Returns:
            The account ID if authenticated, otherwise None.
        """
        return self.auth_service.account_id

    @ApiProviderBase.with_auth_refresh
    def _create_record(
        self,
        project_id: str,
        name: str,
    ) -> str:
        """Create a new workflow in your project.

        Args:
            project_id: Your project's unique identifier
            name: A friendly name for your workflow. This is used to identify the workflow in your project.

        Returns:
            The created workflow ID.
        """

        # Ensure the user has called .auth and the account id is set
        if not self.account_id:
            raise ValueError("Authentication required before reading workflows.")

        # Create the resource record
        workflow_record = WorkflowRecordInput(
            name=name,
            owner_id=self.account_id,
        )
        request_body = PostWorkflowRecordRequest(workflow_record=workflow_record)

        workflow_response = self.workflows_client.post_workflow_record(
            project_id, request_body
        )
        workflow_id = workflow_response.workflow_record.id

        # Ensure workflow ID is valid
        if not workflow_id:
            raise ValueError(
                "Failed to create workflow record. No workflow ID returned."
            )

        return workflow_id

    @ApiProviderBase.with_auth_refresh
    def _create_version(
        self,
        project_id: str,
        workflow_id: str,
        workflow: Workflow,
        version_name: str,
    ) -> str:
        """Create a new version of a workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to create a new version for
            workflow: The workflow object which you wish to save under the version.
            version_name: A name for your version.

        Returns:
            The created version ID.
        """
        # Ensure the user has called .auth and the account id is set
        if not self.account_id:
            raise ValueError(
                "Authentication required before creating workflow versions."
            )

        workflow_version_record = WorkflowVersionRecordInput(
            name=version_name,
            owner_id=self.account_id,
        )
        workflow_version_record = PostWorkflowVersionRequest(
            workflow_version_record=workflow_version_record,
            workflow=workflow.__dict__,
        )

        version_response = self.workflows_client.post_workflow_version(
            project_id, workflow_id, workflow_version_record
        )
        version_id = version_response.workflow_version_record.id

        # Ensure version ID is valid
        if not version_id:
            raise ValueError(
                "Failed to create workflow record version. No version ID returned."
            )

        return version_id

    @ApiProviderBase.with_auth_refresh
    def _read_version(
        self,
        project_id: str,
        workflow_id: str,
        version_id: Optional[str] = None,
    ) -> tuple[WorkflowVersionRecordOutput, Workflow]:
        """Read a workflow version from your project.

        If a version ID is provided, it retrieves that specific version.
        If no version ID is provided, it retrieves the latest version.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read
            version_id: The specific version ID to read. Defaults to none, which retrieves the latest version.

        Returns:
            Workflow: The workflow object containing the details of the workflow.
        """
        # Validate inputs
        if not self.account_id:
            raise ValueError("Authentication required before updating workflows.")

        # Get the resource version and download URL
        if version_id:
            workflow_version_response = self.workflows_client.get_workflow_version(
                project_id, workflow_id, version_id
            )
        else:
            workflow_version_response = (
                self.workflows_client.get_latest_workflow_version(
                    project_id, workflow_id
                )
            )
        version_record = workflow_version_response.workflow_version_record

        if not version_record or not version_record.id:
            raise ValueError(
                "Failed to retrieve workflow version. No version record returned."
            )

        # Extract the workflow data
        workflow_data = workflow_version_response.workflow
        if not workflow_data:
            raise ValueError(
                "No workflow data found in the response. Please check the workflow ID."
            )

        try:
            workflow = Workflow(**workflow_data)
        except Exception as e:
            raise ValueError(
                f"Failed to create Workflow object from response data: {str(e)}"
            )

        return version_record, workflow

    @ApiProviderBase.with_auth_refresh
    def _read_versions(
        self,
        project_id: str,
        workflow_id: str,
    ) -> list[WorkflowVersionRecordOutput]:
        """Read all versions of a workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read versions for

        Returns:
            A list of WorkflowVersionRecordOutput objects representing all versions of the workflow.
        """
        # Validate inputs
        if not self.account_id:
            raise ValueError("Authentication required before reading workflows.")

        versions_response = self.workflows_client.get_workflow_version_records(
            project_id, workflow_id
        )
        return versions_response.workflow_version_records

    @ApiProviderBase.with_auth_refresh
    def _update_version(
        self,
        project_id: str,
        workflow_id: str,
        workflow: Workflow,
        version_id: Optional[str] = None,
    ) -> None:
        """Update a existing version of a workflow in your project.

        If a version ID is provided, it updates that specific version.
        If no version ID is provided, it retrieves the latest version and updates it.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to update
            workflow: The workflow object which you wish to save under the version.
            version_id: The specific version ID to update. Defaults to none, which retrieves the latest version and updates it.
        """

        # Ensure the user has called .auth and the account id is set
        if not self.account_id:
            raise ValueError("Authentication required before updating workflows.")

        # Get the workflow information to create a meaningful version name
        if not version_id:
            latest_version_response = self.workflows_client.get_latest_workflow_version(
                project_id, workflow_id
            )
            version_record = latest_version_response.workflow_version_record
        else:
            version_response = self.workflows_client.get_workflow_version(
                project_id, workflow_id, version_id
            )
            version_record = version_response.workflow_version_record

        # Ensure workflow ID is valid
        if not version_record or not version_record.id:
            raise ValueError(
                "Failed to retrieve workflow. Please ensure the workflow exists."
            )

        workflow_version_record = UpdateWorkflowVersionRequest(
            workflow_version_record_updates=version_record.__dict__,
            workflow=workflow.__dict__,
        )

        # Update existing version
        self.workflows_client.put_workflow_version(
            project_id, workflow_id, version_record.id, workflow_version_record
        )

    @ApiProviderBase.with_auth_refresh
    def save(
        self,
        project_id: str,
        workflow_name: str,
        workflow: Workflow,
        workflow_id: Optional[str] = None,
    ) -> tuple[str, str]:
        """Save a workflow to your project as a new version.

        If a workflow ID is provided, it updates that specific workflow.
        If no workflow ID is provided, it creates a new workflow.

        Args:
            project_id: Your project's unique identifier
            workflow: The workflow object which you wish to save.
            workflow_id: The ID of the workflow you want to update. Defaults to none, which creates a new workflow.

        Returns:
            The ID of the saved workflow.
        """
        try:
            # If no workflow ID, create a new workflow
            if not workflow_id:
                workflow_id = self._create_record(project_id, workflow_name)
                version_name = "version-1"
            else:
                # Ensure a version name is set to version count
                version_count = len(self._read_versions(project_id, workflow_id))
                version_name = f"version-{version_count + 1}"  # Default version name if not provided

            # Create a new version of the workflow
            version_id = self._create_version(
                project_id, workflow_id, workflow, version_name
            )
            return workflow_id, version_id
        except ApiException as e:
            raise Exception(f"Error saving workflow: {format_api_error(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error saving workflow: {str(e)}")

    @ApiProviderBase.with_auth_refresh
    def load(
        self,
        project_id: str,
        workflow_id: str,
        version_id: Optional[str] = None,
    ) -> tuple[WorkflowVersionRecordOutput, Workflow]:
        """Load a workflow from your project.

        If a version ID is provided, it retrieves that specific version.
        If no version ID is provided, it retrieves the latest version.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read
            version_id: The specific version ID to read. Defaults to none, which retrieves the latest version.

        Returns:
            A tuple containing the WorkflowVersionRecordOutput and the Workflow object.
        """
        try:
            return self._read_version(project_id, workflow_id, version_id)
        except ApiException as e:
            raise Exception(f"Error loading workflow: {format_api_error(e)}")
        except ValueError as e:
            raise ValueError(f"Invalid response: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading workflow: {str(e)}")
