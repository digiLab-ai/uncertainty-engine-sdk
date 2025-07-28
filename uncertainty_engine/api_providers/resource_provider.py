import logging
import os
from typing import Any, Optional

import requests
from uncertainty_engine_resource_client.api import ProjectRecordsApi, ResourcesApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostResourceRecordRequest,
    PostResourceVersionRequest,
    ResourceRecordInput,
    ResourceRecordOutput,
    ResourceVersionRecordInput,
)

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.api_providers.constants import DEFAULT_RESOURCE_DEPLOYMENT
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.utils import format_api_error

# Set up logging
logger = logging.getLogger(__name__)


class ResourceProvider(ApiProviderBase):
    """
    Client for managing resources in the Uncertainty Engine platform.

    This client makes it easy to upload, download, update, and list resources
    stored in your Uncertainty Engine projects. Use this client when you need to:

    - Upload resources to your projects for later use
    - Download resources that you or others have previously upload
    - Update existing resources
    - Get a list of available resources in a project

    Before using this client, you'll need a project ID and appropriate access rights.
    """

    def __init__(
        self, auth_service: AuthService, deployment: str = DEFAULT_RESOURCE_DEPLOYMENT
    ):
        """
        Create an instance of a ResourceProvider

        Args:
            auth_service: Handles your authentication.
            deployment: The URL of the resource service. You typically won't need
                        to change this unless instructed by support.
        """
        super().__init__(deployment, auth_service)

        # Initialize the generated API client
        self.client = ApiClient(configuration=Configuration(host=deployment))
        self.projects_client = ProjectRecordsApi(self.client)
        self.resources_client = ResourcesApi(self.client)

        # Update auth headers of the API client (only if authenticated)
        self.update_api_authentication()

    def update_api_authentication(self):
        """Update API client with current auth headers"""
        if self.auth_service.is_authenticated:

            auth_header = self.auth_service.get_auth_header()

            self.client.default_headers.update(auth_header)

            # Update the API instances with the new header
            self.projects_client.api_client.default_headers.update(auth_header)
            self.resources_client.api_client.default_headers.update(auth_header)

    @property
    def account_id(self) -> Optional[str]:
        """
        Get the current account ID from the auth provider

        Returns:
            The account ID if authenticated, otherwise None.
        """
        return self.auth_service.account_id

    @ApiProviderBase.with_auth_refresh
    def upload(
        self,
        project_id: str,
        name: str,
        resource_type: str,
        file_path: str,
    ) -> str:
        """
        Upload a file to your project.

        Use this method when you want to upload a new file to your project for the first time.
        If you're updating an existing file, use the update() method instead.

        Args:
            project_id: Your project's unique identifier
            name: A friendly name for this file (e.g., "2023 Sales Data")
            resource_type: The category for this file (e.g., "dataset", "model", "document")
            file_path: Where the file is on your computer

        Returns:
            A resource ID that you can use later to download or update this file

        Example:
            >>> resource_id = client.upload(
            ...     project_id="your-project-123",
            ...     name="Monthly model",
            ...     resource_type="model",
            ...     file_path="path/to/model.pdf"
            ... )
            >>> print(f"uploaded with ID: {resource_id}")
        """

        # Ensure the user has called .auth and the account id is set
        if not self.account_id:
            raise ValueError("Authentication required before uploading resources")

        file_extension = os.path.splitext(file_path)[1].lstrip(".")

        # Create the resource record
        resource_record = ResourceRecordInput(
            name=name,
            owner_id=self.account_id,
        )
        request_body = PostResourceRecordRequest(resource_record=resource_record)

        try:
            resource_response = self.resources_client.post_resource_record(
                project_id, resource_type, request_body
            )
            resource_id = resource_response.resource_record.id
        except ApiException as e:
            raise Exception(f"Error creating resource record: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error creating resource record: {str(e)}")

        # Create version record and get upload URL
        version_name = f"{name}-v1"
        resource_version_record = ResourceVersionRecordInput(
            name=version_name,
            owner_id=self.account_id,
        )
        resource_version_record = PostResourceVersionRequest(
            resource_version_record=resource_version_record,
            resource_file_extension=file_extension,
        )

        try:
            version_response = self.resources_client.post_resource_version(
                project_id, resource_type, resource_id, resource_version_record
            )
            upload_url = version_response.url
            pending_id = version_response.pending_record_id
        except ApiException as e:
            raise Exception(f"Error creating version record: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error creating version record: {str(e)}")

        # Upload the file to the presigned URL
        try:
            with open(file_path, "rb") as file:
                response = requests.put(upload_url, data=file)

                if response.status_code != 200:
                    raise Exception(
                        f"Upload failed with status {response.status_code}: {response.text}"
                    )

        except Exception as e:
            raise Exception(f"Error uploading file to presigned URL: {str(e)}")

        # Complete the upload process
        try:
            self.resources_client.put_upload_resource_version(
                project_id, resource_type, resource_id, pending_id
            )
        except ApiException as e:
            raise Exception(f"Error completing upload: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error completing upload: {str(e)}")

        return resource_id

    @ApiProviderBase.with_auth_refresh
    def download(
        self,
        project_id: str,
        resource_type: str,
        resource_id: str,
        file_path: Optional[str] = None,
    ) -> Optional[Any]:
        """
        Download a file from your project to your computer.

        This always downloads the latest version of the file. The method will create
        any folders needed to download the file at the location you specify.

        If a file path is not provided this function will, instead, return the raw
        resource content.

        Args:
            project_id: Your project's unique identifier
            resource_type: The category of the file (e.g., "dataset", "model", "document")
            resource_id: The ID of the file you want to download
            file_path: Where to upload the file on your computer

        Returns:
            resource - If no filepath has been provided

        Example:
            >>> client.download(
            ...     project_id="your-project-123",
            ...     resource_type="model",
            ...     resource_id="resource-456",
            ...     file_path="downloads/model.json"
            ... )
        """
        # Validate inputs
        if not self.account_id:
            raise ValueError("Authentication required before downloading resources")

        # Create directory if it doesn't exist
        if file_path:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # Get the resource version and download URL
        try:
            resource_response = self.resources_client.get_latest_resource_version(
                project_id, resource_type, resource_id
            )
            download_url = resource_response.url
        except ApiException as e:
            raise Exception(f"Error retrieving resource: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error retrieving resource: {str(e)}")

        try:
            response = requests.get(download_url)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except Exception as e:
            raise Exception(f"Error saving downloaded file: {str(e)}")

        if file_path:
            # If a filepath is provided save the file to the provided path
            with open(file_path, "wb") as file:
                file.write(response.content)
        else:
            # Otherwise return the response content
            return response.content

    @ApiProviderBase.with_auth_refresh
    def update(
        self,
        project_id: str,
        resource_type: str,
        resource_id: str,
        file_path: str,
    ) -> None:
        """
        Upload a new version of an existing resource.

        Use this method when you want to update a resource that's already in your project.
        The system will keep all previous versions, but this new version becomes the default.

        Args:
            project_id: Your project's unique identifier
            resource_type: The category of the file (e.g., "dataset", "model", "document")
            resource_id: The ID of the resource you want to update
            file_path: Where the new version is on your computer

        Example:
            >>> client.update(
            ...     project_id="your-project-123",
            ...     resource_type="model",
            ...     resource_id="resource-456",
            ...     file_path="path/to/updated_model.json"
            ... )
            >>> print("Successfully updated the file")
        """

        # Ensure the user has called .auth and the account id is set
        if not self.account_id:
            raise ValueError("Authentication required before updating resources")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_extension = os.path.splitext(file_path)[1].lstrip(".")

        # Get the resource information to create a meaningful version name
        try:
            resource = self.resources_client.get_resource_record(
                project_id, resource_type, resource_id
            )
            resource_name = resource.resource_record.name
            version_count = len(resource.resource_record.versions)
            version_name = f"{resource_name}-v{version_count + 1}"
        except Exception:
            raise Exception(
                "Unable to retrieve resource record. Please ensure the resource exists before attempting to update it."
            )
        resource_version_record = PostResourceVersionRequest(
            resource_version_record=ResourceVersionRecordInput(
                name=version_name,
                owner_id=self.account_id,
            ),
            resource_file_extension=file_extension,
        )

        try:
            version_response = self.resources_client.post_resource_version(
                project_id, resource_type, resource_id, resource_version_record
            )
            upload_url = version_response.url
            pending_id = version_response.pending_record_id
        except ApiException as e:
            raise Exception(f"Error creating version record: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error creating version record: {str(e)}")

        # Upload the file to the presigned URL
        try:
            with open(file_path, "rb") as file:
                response = requests.put(upload_url, data=file)

                if response.status_code != 200:
                    raise Exception(
                        f"Upload failed with status {response.status_code}: {response.text}"
                    )

        except Exception as e:
            raise Exception(f"Error uploading file to presigned URL: {str(e)}")

        # Complete the upload process
        try:
            self.resources_client.put_upload_resource_version(
                project_id, resource_type, resource_id, pending_id
            )
        except ApiException as e:
            raise Exception(f"Error finalizing upload: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error finalizing upload: {str(e)}")

    @ApiProviderBase.with_auth_refresh
    def list_resources(
        self, project_id: str, resource_type: str
    ) -> list[ResourceRecordOutput]:
        """
        Get a list of all resources of a specific type in your project.

        This is useful when you need to see what resources are available or when
        you want to find a specific file's ID for downloading.

        Args:
            project_id: Your project's unique identifier
            resource_type: The category of resources to list (e.g., "dataset", "model")

        Returns:
            A list of all matching resources with their details

        Example:
            >>> models = client.resources.list_resources(
            ...     project_id="your-project-123",
            ...     resource_type="model"
            ... )
            >>> print(f"Found {len(models)} models")
            >>> print(models)
        """

        try:

            resource_records = self.resources_client.get_project_resource_records(
                project_id, resource_type
            ).resource_records
            return [
                ResourceRecordOutput.model_validate(record)
                for record in resource_records
            ]
        except ApiException as e:
            raise Exception(f"Error listing resource records: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error listing resource records: {str(e)}")

    @ApiProviderBase.with_auth_refresh
    def delete_resource(
        self, project_id: str, resource_type: str, resource_id: str
    ) -> None:
        """
        Delete a resource from your project.

        Use this method when you want to permanently remove a resource from your project.
        Be cautious, as this action cannot be undone.

        Args:
            project_id: Your project's unique identifier
            resource_type: The category of the file (e.g., "dataset", "model", "document")
            resource_id: The ID of the resource you want to delete

        Example:
            >>> client.resources.delete_resource(
            ...     project_id="your-project-123",
            ...     resource_type="model",
            ...     resource_id="resource-456"
            ... )
            # Will add INFO level log -- "Resource resource-456 deleted successfully from project your-project-123."
        """
        try:
            self.resources_client.delete_resource_record(
                project_id, resource_type, resource_id
            )
        except ApiException as e:
            raise Exception(f"Error deleting resource: {format_api_error(e)}")
        except Exception as e:
            raise Exception(f"Error deleting resource: {str(e)}")

        logger.info(
            f"Resource {resource_id} deleted successfully from project {project_id}."
        )
