from typing import Optional

from uncertainty_engine_resource_client.api import ProjectRecordsApi, WorkflowsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostWorkflowRecordRequest,
    PostWorkflowVersionRequest,
    WorkflowRecordInput,
    WorkflowRecordOutput,
    WorkflowVersionRecordInput,
    WorkflowVersionRecordOutput,
)

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.api_providers.constants import (
    DATETIME_STRING_FORMAT,
    DEFAULT_RESOURCE_DEPLOYMENT,
)
from uncertainty_engine.api_providers.models import (
    WorkflowExecutable,
    WorkflowRecord,
    WorkflowVersion,
)
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.nodes.workflow import Workflow
from uncertainty_engine.utils import format_api_error
from pydantic import ValidationError


class WorkflowsProvider(ApiProviderBase):
    """
    Client for managing workflows in the Uncertainty Engine platform.

    This client makes it easy to save and load workflows stored in your
    Uncertainty Engine projects. Use this client when you need to:

    - List all workflows in your projects
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

        # Initialize low-level record and version management
        self._record_manager = RecordManager(self.workflows_client, self.auth_service)
        self._version_manager = VersionManager(self.workflows_client, self.auth_service)

        # Update auth headers of the API client (only if authenticated)
        self.update_api_authentication()

    def update_api_authentication(self) -> None:  # type: ignore
        """Update API client with current auth headers"""
        if self.auth_service.is_authenticated:

            auth_header = self.auth_service.get_auth_header()

            self.client.default_headers.update(auth_header)

            # Update the API instances with the new header
            self.projects_client.api_client.default_headers.update(auth_header)
            self.workflows_client.api_client.default_headers.update(auth_header)

    @property
    def account_id(self) -> Optional[str]:
        """
        Get the current account ID from the auth provider

        Returns:
            The account ID if authenticated, otherwise None.
        """
        return self.auth_service.account_id

    @ApiProviderBase.with_auth_refresh
    def list_workflows(
        self,
        project_id: str,
    ) -> list[WorkflowRecord]:
        """
        List all workflows in your project.

        Args:
            project_id: Your project's unique identifier

        Returns:
            A list of dictionaries containing workflow details, each with:
                - id: The unique identifier of the workflow
                - name: The friendly name of the workflow
                - owner_id: The ID of the user who owns the workflow
                - created_at: The creation date of the workflow in ISO 8601 format
                - versions: A list of version IDs associated with the workflow
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError("Authentication required before listing workflows.")

        return [
            WorkflowRecord(
                id=record.id,
                name=record.name,
                owner_id=record.owner_id,
                created_at=(
                    record.created_at.strftime(DATETIME_STRING_FORMAT)
                    if record.created_at
                    else None
                ),
                versions=record.versions if record.versions else [],
            )
            for record in self._record_manager.list_records(project_id)
        ]

    @ApiProviderBase.with_auth_refresh
    def list_workflow_versions(
        self,
        project_id: str,
        workflow_id: str,
    ) -> list[WorkflowVersion]:
        """
        List all versions of a workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read versions for

        Returns:
            A list of dictionaries containing workflow version details, each with:
                - id: The version ID
                - workflow_id: The ID of the workflow this version belongs to
                - name: The version name
                - owner_id: The ID of the owner of the version (who created it)
                - created_at: The creation date of the version in ISO format
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError(
                "Authentication required before listing workflow versions."
            )

        return [
            WorkflowVersion(
                id=version.id,
                workflow_id=version.workflow_id,
                name=version.name,
                owner_id=version.owner_id,
                created_at=(
                    version.created_at.strftime(DATETIME_STRING_FORMAT)
                    if version.created_at
                    else None
                ),
            )
            for version in self._version_manager.list_versions(project_id, workflow_id)
        ]

    @ApiProviderBase.with_auth_refresh
    def load(
        self,
        project_id: str,
        workflow_id: str,
        version_id: Optional[str] = None,
    ) -> Workflow:
        """
        Load a workflow from your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read
            version_id: The specific version ID to read. Defaults to none, which retrieves the latest version.

        Returns:
            The loaded Workflow object.
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError("Authentication required before loading workflows.")

        executable_workflow = self._version_manager.read_version(
            project_id, workflow_id, version_id
        )
        workflow = executable_workflow.inputs

        return Workflow(
            graph=workflow["graph"],
            input=workflow["inputs"],
            requested_output=workflow["requested_output"],
            external_input_id=workflow["external_input_id"],
        )

    @ApiProviderBase.with_auth_refresh
    def save(
        self,
        project_id: str,
        workflow: Workflow,
        workflow_id: Optional[str] = None,
        workflow_name: Optional[str] = None,
    ) -> str:
        """
        Save a workflow to your project as a new version.

        Args:
            project_id: Your project's unique identifier
            workflow: The workflow object which you wish to save.
            workflow_name: A friendly name for your workflow. This needs to be unique within the project.
                           Defaults to none, however must be provided when creating a new workflow.
                           Note that it will be ignored if provided when updating an existing workflow.
            workflow_id: The ID of the workflow you want to update. Defaults to none, which creates a new workflow.

        Returns:
            The ID of the saved workflow.
        """
        # Check if account ID is set
        if not self.account_id:
            raise ValueError("Authentication required before saving workflows.")

        # If no workflow ID, create a new workflow
        if not workflow_id:
            if not workflow_name:
                raise ValueError(
                    "workflow_name must be provided to create a new workflow."
                )
            workflow_id = self._record_manager.create_record(project_id, workflow_name)

        executable_workflow = (
            WorkflowExecutable(  # Workflow must be wrapped by this to be executable
                node_id="Workflow",
                inputs=workflow.__dict__,
            )
        )

        # Create a new version of the workflow
        self._version_manager.create_version(
            project_id, workflow_id, executable_workflow
        )
        return workflow_id


class RecordManager:
    """
    A class to manage workflow records.
    This class provides methods to create and read workflow versions.
    It is used internally by the WorkflowsProvider class.
    """

    def __init__(self, workflows_client: WorkflowsApi, auth_service: AuthService):
        """Initialize the RecordManager with a WorkflowsProvider instance.

        Args:
            workflows_provider: An instance of WorkflowsProvider to manage workflow records.
        """
        self.workflows_client = workflows_client
        self.auth_service = auth_service

    def create_record(
        self,
        project_id: str,
        workflow_name: str,
    ) -> str:
        """
        Create a new workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_name: A friendly name for your workflow. This must be unique within your project.

        Returns:
            The created workflow ID.
        """
        # Create the resource record
        workflow_record = WorkflowRecordInput(
            name=workflow_name,
            owner_id=self.auth_service.account_id,
        )
        request_body = PostWorkflowRecordRequest(workflow_record=workflow_record)

        try:
            workflow_response = self.workflows_client.post_workflow_record(
                project_id, request_body
            )
            workflow_id = workflow_response.workflow_record.id

            # Ensure workflow ID is valid
            if not workflow_id:
                raise ValueError("No workflow ID returned.")

            return workflow_id
        except ApiException as e:
            raise Exception(f"Error creating workflow record: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error creating workflow record: {str(e)}")

    def list_records(
        self,
        project_id: str,
    ) -> list[WorkflowRecordOutput]:
        """
        Read all workflow records in your project.

        Args:
            project_id: Your project's unique identifier

        Returns:
            A list of WorkflowVersionRecordOutput objects representing all workflows in the project.
        """
        try:
            records_response = self.workflows_client.get_project_workflow_records(
                project_id
            )
            return records_response.workflow_records
        except ApiException as e:
            raise Exception(f"Error reading workflow records: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error reading workflow records: {str(e)}")


class VersionManager:
    """
    A class to manage workflow versions.
    This class provides methods to create, read, and list workflow versions.
    It is used internally by the WorkflowsProvider class.
    """

    def __init__(self, workflows_client: WorkflowsApi, auth_service: AuthService):
        """
        Initialize the VersionManager with a WorkflowsProvider instance.

        Args:
            workflows_provider: An instance of WorkflowsProvider to manage workflow versions.
        """
        self.workflows_client = workflows_client
        self.auth_service = auth_service

    def create_version(
        self,
        project_id: str,
        workflow_id: str,
        workflow: WorkflowExecutable,
        version_name: Optional[str] = None,
    ) -> str:
        """
        Create a new version of a workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to create a new version for
            workflow: The workflow object which you wish to save under the version.
            version_name: A name for your version. Defaults to "version-{version-count}" if not provided.

        Returns:
            The created version ID.
        """
        try:
            # If no version name is provided, default to "version-1"
            if not version_name:
                version_count = len(self.list_versions(project_id, workflow_id))
                version_name = f"version-{version_count + 1}"

            workflow_version_record = WorkflowVersionRecordInput(
                name=version_name,
                owner_id=self.auth_service.account_id,
            )
            workflow_version_record = PostWorkflowVersionRequest(
                workflow_version_record=workflow_version_record,
                workflow=workflow.model_dump(),
            )

            version_response = self.workflows_client.post_workflow_version(
                project_id, workflow_id, workflow_version_record
            )
            version_id = version_response.workflow_version_record.id

            # Ensure version ID is valid
            if not version_id:
                raise ValueError("No version ID returned.")

            return version_id
        except ApiException as e:
            raise Exception(f"Error creating workflow version: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error creating workflow version: {str(e)}")

    def read_version(
        self,
        project_id: str,
        workflow_id: str,
        version_id: Optional[str] = None,
    ) -> WorkflowExecutable:
        """
        Read a workflow version from your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read
            version_id: The specific version ID to read. Defaults to none, which retrieves the latest version.

        Returns:
            Workflow: The workflow object containing the details of the workflow.
        """
        try:
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
            # Extract the workflow data
            workflow_data = workflow_version_response.workflow
            if not workflow_data:
                raise ValueError("No workflow data found in the response.")

            # Convert the workflow data to a ExecutableWorkflow object
            # KeyError will be raised if the data is not compatible (old version of the workflow)
            workflow = WorkflowExecutable(**workflow_data)

            return workflow
        except ApiException as e:
            raise Exception(f"Error reading workflow version: {format_api_error(e)}")
        except (KeyError, ValidationError) as e:
            raise KeyError(f"Invalid Workflow object structure: {e}")
        except Exception as e:
            raise Exception(f"Error reading workflow version: {str(e)}")

    def list_versions(
        self,
        project_id: str,
        workflow_id: str,
    ) -> list[WorkflowVersionRecordOutput]:
        """
        Read all versions of a workflow in your project.

        Args:
            project_id: Your project's unique identifier
            workflow_id: The ID of the workflow you want to read versions for

        Returns:
            A list of WorkflowVersionRecordOutput objects representing all versions of the workflow.
        """
        try:
            versions_response = self.workflows_client.get_workflow_version_records(
                project_id, workflow_id
            )
            return versions_response.workflow_version_records
        except ApiException as e:
            raise Exception(f"Error reading workflow versions: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error reading workflow versions: {str(e)}")
