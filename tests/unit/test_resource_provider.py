import os
import pytest
from unittest.mock import MagicMock, patch, mock_open
from datetime import datetime

import requests
from uncertainty_engine_resource_client.api import ProjectRecordsApi, ResourcesApi
from uncertainty_engine_resource_client.models import (
    PostResourceRecordRequest,
    PostResourceVersionRequest,
    ResourceRecordInput,
    ResourceVersionRecordInput,
)
from uncertainty_engine_resource_client.exceptions import ApiException

from uncertainty_engine.api_providers import ResourceProvider
from uncertainty_engine.api_providers.resource_provider import (
    DEFAULT_RESOURCE_DEPLOYMENT,
    DATETIME_STRING_FORMAT,
)


@pytest.fixture
def mock_auth_provider():
    """Fixture for a mock authentication provider."""
    auth_provider = MagicMock()
    auth_provider.account_id = "test-account-id"
    return auth_provider


@pytest.fixture
def mock_api_client():
    """Fixture for a mock API client."""
    return MagicMock()


@pytest.fixture
def mock_projects_client():
    """Fixture for a mock projects client."""
    return MagicMock()


@pytest.fixture
def mock_resources_client():
    """Fixture for a mock resources client."""
    return MagicMock()


@pytest.fixture
def resource_provider(
    mock_auth_provider, mock_api_client, mock_projects_client, mock_resources_client
):
    """Fixture for a ResourceProvider with mocked dependencies."""
    with patch(
        "uncertainty_engine_resource_client.ApiClient", return_value=mock_api_client
    ):
        with patch.object(ProjectRecordsApi, "__init__", return_value=None):
            with patch.object(ResourcesApi, "__init__", return_value=None):
                provider = ResourceProvider(auth_provider=mock_auth_provider)
                provider.projects_client = mock_projects_client
                provider.resources_client = mock_resources_client
                return provider


def test_init_default():
    """Test initializing with default parameters."""
    with patch("uncertainty_engine_resource_client.ApiClient") as mock_client:
        with patch("uncertainty_engine_resource_client.Configuration") as mock_config:
            with patch.object(ProjectRecordsApi, "__init__", return_value=None):
                with patch.object(ResourcesApi, "__init__", return_value=None):
                    provider = ResourceProvider()

                    # Verify configuration is created with default URL
                    mock_config.assert_called_once_with(
                        host=DEFAULT_RESOURCE_DEPLOYMENT
                    )

                    # Verify clients are created
                    mock_client.assert_called_once()
                    assert provider.auth_provider is None
                    assert provider.client is not None
                    assert provider.projects_client is not None
                    assert provider.resources_client is not None


def test_init_custom(mock_auth_provider):
    """Test initializing with custom parameters."""
    custom_url = "http://custom-url.com"

    with patch("uncertainty_engine_resource_client.ApiClient") as mock_client:
        with patch("uncertainty_engine_resource_client.Configuration") as mock_config:
            with patch.object(ProjectRecordsApi, "__init__", return_value=None):
                with patch.object(ResourcesApi, "__init__", return_value=None):
                    provider = ResourceProvider(
                        deployment=custom_url, auth_provider=mock_auth_provider
                    )

                    # Verify configuration is created with custom URL
                    mock_config.assert_called_once_with(host=custom_url)

                    # Verify clients are created
                    mock_client.assert_called_once()
                    assert provider.auth_provider is mock_auth_provider
                    assert provider.client is not None


def test_account_id_with_auth_provider(resource_provider, mock_auth_provider):
    """Test the account_id property when auth_provider is available."""
    assert resource_provider.account_id == mock_auth_provider.account_id


def test_account_id_without_auth_provider():
    """Test the account_id property when auth_provider is not available."""
    with patch("uncertainty_engine_resource_client.ApiClient"):
        with patch.object(ProjectRecordsApi, "__init__", return_value=None):
            with patch.object(ResourcesApi, "__init__", return_value=None):
                provider = ResourceProvider(auth_provider=None)
                assert provider.account_id is None


def test_upload_success(resource_provider, mock_resources_client):
    """Test the upload method when successful."""
    # Setup mock responses
    resource_record = MagicMock(id="test-resource-id")
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.post_resource_record.return_value = resource_response

    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"test file content")

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Test parameters
    project_id = "test-project"
    name = "Test Resource"
    resource_type = "dataset"
    file_path = "path/to/test_file.csv"

    with patch("builtins.open", mock_file):
        with patch("requests.put", return_value=mock_put_response):
            # Call the method
            result = resource_provider.upload(
                project_id=project_id,
                name=name,
                resource_type=resource_type,
                file_path=file_path,
            )

            # Verify the result
            assert result == "test-resource-id"

            # Verify method calls
            mock_resources_client.post_resource_record.assert_called_once_with(
                project_id,
                resource_type,
                PostResourceRecordRequest(
                    resource_record=ResourceRecordInput(
                        name=name, owner_id=resource_provider.account_id
                    )
                ),
            )

            mock_resources_client.post_resource_version.assert_called_once_with(
                project_id,
                resource_type,
                "test-resource-id",
                PostResourceVersionRequest(
                    resource_version_record=ResourceVersionRecordInput(
                        name=f"{name}-v1", owner_id=resource_provider.account_id
                    ),
                    resource_file_extension="csv",
                ),
            )

            mock_file.assert_called_once_with(file_path, "rb")
            requests.put.assert_called_once_with(
                "https://upload-url.com", data=mock_file()
            )

            mock_resources_client.put_upload_resource_version.assert_called_once_with(
                project_id, resource_type, "test-resource-id", "test-pending-id"
            )


def test_upload_no_auth(resource_provider):
    """Test upload fails when not authenticated."""

    # Set auth provider to None
    with patch.object(resource_provider, "auth_provider", None):

        # Call and verify exception
        with pytest.raises(
            ValueError, match="Authentication required before uploading resources"
        ):
            resource_provider.upload("project-id", "name", "type", "path")


def test_upload_api_exception_on_record_creation(
    resource_provider, mock_resources_client
):
    """Test handling of ApiException during resource record creation."""
    # Setup mock error
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.post_resource_record.side_effect = api_exception

    # Call and verify exception
    with pytest.raises(Exception, match="Error creating resource record:"):
        resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


def test_upload_api_exception_on_version_creation(
    resource_provider, mock_resources_client
):
    """Test handling of ApiException during version record creation."""
    # Setup mocks
    resource_record = MagicMock(id="test-resource-id")
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.post_resource_record.return_value = resource_response

    # Setup exception
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.post_resource_version.side_effect = api_exception

    # Call and verify exception
    with pytest.raises(Exception, match="Error creating version record:"):
        resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


def test_upload_failed_file_upload(resource_provider, mock_resources_client):
    """Test handling of failed upload to presigned URL."""
    # Setup mocks
    resource_record = MagicMock(id="test-resource-id")
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.post_resource_record.return_value = resource_response

    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"test file content")

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = 403
    mock_put_response.text = "Forbidden"

    with patch("builtins.open", mock_file):
        with patch("requests.put", return_value=mock_put_response):
            # Call and verify exception
            with pytest.raises(
                Exception, match="Upload failed with status 403: Forbidden"
            ):
                resource_provider.upload(
                    "project-id", "name", "type", "path/to/file.txt"
                )


def test_upload_failed_completion(resource_provider, mock_resources_client):
    """Test handling of exception during upload completion."""
    # Setup mocks
    resource_record = MagicMock(id="test-resource-id")
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.post_resource_record.return_value = resource_response

    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"test file content")

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Setup exception on completion
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.put_upload_resource_version.side_effect = api_exception

    with patch("builtins.open", mock_file):
        with patch("requests.put", return_value=mock_put_response):
            # Call and verify exception
            with pytest.raises(Exception, match="Error completing upload:"):
                resource_provider.upload(
                    "project-id", "name", "type", "path/to/file.txt"
                )


def test_download_success_with_filepath(resource_provider):
    """Test downloading a resource with a specified filepath."""
    # Setup mocks
    version_response = MagicMock()
    version_response.url = "https://download-url.com"
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    # Setup file mock
    mock_file = mock_open()

    with patch("os.makedirs") as mock_makedirs:
        with patch("builtins.open", mock_file):
            with patch("requests.get", return_value=mock_get_response):
                # Call the method
                resource_provider.download(
                    project_id="test-project",
                    resource_type="dataset",
                    resource_id="test-resource-id",
                    file_path="path/to/download/file.csv",
                )

                # Verify method calls
                resource_provider.resources_client.get_latest_resource_version.assert_called_once_with(
                    "test-project", "dataset", "test-resource-id"
                )

                mock_makedirs.assert_called_once_with(
                    os.path.dirname(os.path.abspath("path/to/download/file.csv")),
                    exist_ok=True,
                )
                requests.get.assert_called_once_with("https://download-url.com")
                mock_get_response.raise_for_status.assert_called_once()
                mock_file.assert_called_once_with("path/to/download/file.csv", "wb")
                mock_file().write.assert_called_once_with(b"test file content")


def test_download_success_without_filepath(resource_provider):
    """Test downloading a resource without a specified filepath (return content)."""
    # Setup mocks
    version_response = MagicMock()
    version_response.url = "https://download-url.com"
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    expected_content = b'{"data": "test content"}'
    mock_get_response.content = expected_content

    with patch("requests.get", return_value=mock_get_response):
        # Call the method
        result = resource_provider.download(
            project_id="test-project",
            resource_type="dataset",
            resource_id="test-resource-id",
        )

        # Verify result and method calls
        assert result == expected_content
        resource_provider.resources_client.get_latest_resource_version.assert_called_once_with(
            "test-project", "dataset", "test-resource-id"
        )
        requests.get.assert_called_once_with("https://download-url.com")
        mock_get_response.raise_for_status.assert_called_once()


def test_download_no_auth(resource_provider):
    """Test download fails when not authenticated."""
    # Set auth provider to None
    with patch.object(resource_provider, "auth_provider", None):

        # Call and verify exception
        with pytest.raises(
            ValueError, match="Authentication required before downloading resources"
        ):
            resource_provider.download("project-id", "type", "resource-id")


def test_download_api_exception(resource_provider):
    """Test handling of ApiException during resource version retrieval."""
    # Setup exception
    api_exception = ApiException(status=404, reason="Not Found")
    resource_provider.resources_client.get_latest_resource_version.side_effect = (
        api_exception
    )

    # Call and verify exception
    with pytest.raises(Exception, match="Error retrieving resource:"):
        resource_provider.download(
            "project-id", "type", "resource-id", "path/to/file.txt"
        )


def test_download_generic_exception_on_retrieval(resource_provider):
    """Test handling of generic Exception during resource retrieval."""
    # Setup exception
    generic_exception = Exception("Random error")
    resource_provider.resources_client.get_latest_resource_version.side_effect = (
        generic_exception
    )

    # Call and verify exception
    with pytest.raises(Exception, match="Error retrieving resource: Random error"):
        resource_provider.download(
            "project-id", "type", "resource-id", "path/to/file.txt"
        )


def test_download_http_error(resource_provider):
    """Test handling of HTTP error during download."""
    # Setup mocks
    version_response = MagicMock()
    version_response.url = "https://download-url.com"
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        version_response
    )

    # Setup requests mock with error
    mock_get_response = MagicMock()
    http_error = requests.exceptions.HTTPError("404 Client Error")
    mock_get_response.raise_for_status.side_effect = http_error

    with patch("requests.get", return_value=mock_get_response):
        # Call and verify exception
        with pytest.raises(Exception, match="Error saving downloaded file:"):
            resource_provider.download(
                "project-id", "type", "resource-id", "path/to/file.txt"
            )


def test_download_file_not_found_error(resource_provider):
    """Test handling of FileNotFoundError when writing to a file."""
    # Setup mocks
    version_response = MagicMock()
    version_response.url = "https://download-url.com"
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    # Setup file mock to raise FileNotFoundError
    mock_file = mock_open()
    mock_file.side_effect = FileNotFoundError("No such file or directory")

    with patch("os.makedirs"):
        with patch("builtins.open", mock_file):
            with patch("requests.get", return_value=mock_get_response):
                # Call and verify exception
                with pytest.raises(Exception, match="Invalid filepath provided"):
                    resource_provider.download(
                        project_id="test-project",
                        resource_type="dataset",
                        resource_id="test-resource-id",
                        file_path="path/to/download/file.csv",
                    )

                mock_get_response.raise_for_status.assert_called_once()


def test_download_other_file_exception(resource_provider):
    """Test handling of generic exceptions when writing to a file."""
    # Setup mocks
    version_response = MagicMock()
    version_response.url = "https://download-url.com"
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    # Setup file mock to raise a permission error - this is more specific and appropriate
    mock_file = mock_open()
    # Configure the write method to raise the exception
    mock_file.return_value.write.side_effect = PermissionError("Permission denied")

    with patch("os.makedirs"):
        with patch("builtins.open", mock_file):
            with patch("requests.get", return_value=mock_get_response):
                # Call and verify exception
                with pytest.raises(PermissionError, match="Permission denied"):
                    resource_provider.download(
                        project_id="test-project",
                        resource_type="dataset",
                        resource_id="test-resource-id",
                        file_path="path/to/download/file.csv",
                    )


# def test_download_content_processing_error(resource_provider):
#     """Test handling of errors when processing content without a filepath."""
#     # Setup mocks
#     version_response = MagicMock()
#     version_response.url = "https://download-url.com"
#     resource_provider.resources_client.get_latest_resource_version.return_value = (
#         version_response
#     )

#     # Setup requests mock with an error in both json() and text
#     mock_get_response = MagicMock()
#     mock_get_response.json.side_effect = JSONDecodeError("Invalid JSON", "", 0)

#     # Replace the text attribute with a PropertyMock that raises an exception
#     text_property = PropertyMock(
#         side_effect=Exception("Error returning resource content")
#     )
#     type(mock_get_response).text = text_property

#     with patch("requests.get", return_value=mock_get_response):
#         # Call and verify exception
#         with pytest.raises(Exception, match="Error returning resource content"):
#             resource_provider.download(
#                 project_id="test-project",
#                 resource_type="dataset",
#                 resource_id="test-resource-id",
#             )

#         mock_get_response.raise_for_status.assert_called_once()


def test_update_success(resource_provider, mock_resources_client):
    """Test updating a resource successfully."""
    # Setup mocks for resource info with direct attribute assignment
    resource_record = MagicMock()
    resource_record.name = "Test Resource"  # Direct assignment for string value
    resource_record.versions = ["v1", "v2"]

    resource_response = MagicMock()
    resource_response.resource_record = resource_record
    mock_resources_client.get_resource_record.return_value = resource_response

    # Setup mocks for version creation
    version_response = MagicMock()
    version_response.url = "https://upload-url.com"
    version_response.pending_record_id = "test-pending-id"
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"updated content")

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                # Call the method
                resource_provider.update(
                    project_id="test-project",
                    resource_type="dataset",
                    resource_id="test-resource-id",
                    file_path="path/to/updated_file.json",
                )

                # Verify method calls
                mock_resources_client.get_resource_record.assert_called_once_with(
                    "test-project", "dataset", "test-resource-id"
                )

                # Expected version name should be resource name + v3 (since there are two existing versions)
                mock_resources_client.post_resource_version.assert_called_once_with(
                    "test-project",
                    "dataset",
                    "test-resource-id",
                    PostResourceVersionRequest(
                        resource_version_record=ResourceVersionRecordInput(
                            name="Test Resource-v3",
                            owner_id=resource_provider.account_id,
                        ),
                        resource_file_extension="json",
                    ),
                )

                mock_file.assert_called_once_with("path/to/updated_file.json", "rb")
                requests.put.assert_called_once_with(
                    "https://upload-url.com", data=mock_file()
                )

                mock_resources_client.put_upload_resource_version.assert_called_once_with(
                    "test-project", "dataset", "test-resource-id", "test-pending-id"
                )


def test_update_resource_not_found(resource_provider, mock_resources_client):
    """Test handling when the resource to update is not found."""
    # Setup exception for resource lookup
    api_exception = ApiException(status=404, reason="Not Found")
    mock_resources_client.get_resource_record.side_effect = api_exception

    # Setup mocks for version creation
    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"updated content")

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                with patch(
                    "uncertainty_engine.resource_provider.uuid4",
                    return_value="test-uuid",
                ):
                    # Call the method
                    resource_provider.update(
                        project_id="test-project",
                        resource_type="dataset",
                        resource_id="test-resource-id",
                        file_path="path/to/updated_file.json",
                    )

                    # Verify the generic version name is used
                    mock_resources_client.post_resource_version.assert_called_once_with(
                        "test-project",
                        "dataset",
                        "test-resource-id",
                        PostResourceVersionRequest(
                            resource_version_record=ResourceVersionRecordInput(
                                name="version-test-uuid",
                                owner_id=resource_provider.account_id,
                            ),
                            resource_file_extension="json",
                        ),
                    )


def test_update_no_auth(resource_provider):
    """Test update fails when not authenticated."""
    # Set auth provider to None
    with patch.object(resource_provider, "auth_provider", None):
        resource_provider.auth_provider = None

        # Call and verify exception
        with pytest.raises(
            ValueError, match="Authentication required before updating resources"
        ):
            resource_provider.update(
                "project-id", "type", "resource-id", "path/to/file.txt"
            )


def test_update_file_not_found(resource_provider):
    """Test update fails when the file doesn't exist."""
    with patch("os.path.exists", return_value=False):
        # Call and verify exception
        with pytest.raises(FileNotFoundError, match="File not found:"):
            resource_provider.update(
                "project-id", "type", "resource-id", "nonexistent/file.txt"
            )


def test_update_api_exception_on_version_creation(
    resource_provider, mock_resources_client
):
    """Test handling of ApiException during version record creation."""
    # Setup mocks for resource info
    resource_record = MagicMock(name="Test Resource", versions=["v1"])
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.get_resource_record.return_value = resource_response

    # Setup exception for version creation
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.post_resource_version.side_effect = api_exception

    with patch("os.path.exists", return_value=True):
        # Call and verify exception
        with pytest.raises(Exception, match="Error creating version record:"):
            resource_provider.update(
                "project-id", "type", "resource-id", "path/to/file.txt"
            )


def test_update_upload_error(resource_provider, mock_resources_client):
    """Test handling of error during upload to presigned URL."""
    # Setup mocks for resource info
    resource_record = MagicMock(name="Test Resource", versions=["v1"])
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.get_resource_record.return_value = resource_response

    # Setup mocks for version creation
    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"updated content")

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = 403
    mock_put_response.text = "Forbidden"

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                # Call and verify exception
                with pytest.raises(
                    Exception, match="Upload failed with status 403: Forbidden"
                ):
                    resource_provider.update(
                        "test-project",
                        "dataset",
                        "test-resource-id",
                        "path/to/updated_file.json",
                    )


def test_update_finalize_error(resource_provider, mock_resources_client):
    """Test handling of error during finalization of upload."""
    # Setup mocks for resource info
    resource_record = MagicMock(name="Test Resource", versions=["v1"])
    resource_response = MagicMock(resource_record=resource_record)
    mock_resources_client.get_resource_record.return_value = resource_response

    # Setup mocks for version creation
    version_response = MagicMock(
        url="https://upload-url.com", pending_record_id="test-pending-id"
    )
    mock_resources_client.post_resource_version.return_value = version_response

    # Setup file mock
    mock_file = mock_open(read_data=b"updated content")

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Setup exception for finalization
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.put_upload_resource_version.side_effect = api_exception

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                # Call and verify exception
                with pytest.raises(Exception, match="Error finalizing upload:"):
                    resource_provider.update(
                        "test-project",
                        "dataset",
                        "test-resource-id",
                        "path/to/updated_file.json",
                    )


def test_list_success(resource_provider, mock_resources_client):
    """Test listing resources successfully."""
    # Setup mock response
    created_time = datetime.now()

    # Create proper mock objects with attributes that return expected values
    record1 = MagicMock()
    record1.id = "resource-1"  # Direct assignment to make it return the string
    record1.name = "Resource 1"
    record1.created_at = created_time

    record2 = MagicMock()
    record2.id = "resource-2"
    record2.name = "Resource 2"
    record2.created_at = created_time

    resource_records = [record1, record2]
    response = MagicMock(resource_records=resource_records)
    mock_resources_client.get_project_resource_records.return_value = response

    # Call the method
    result = resource_provider.list("test-project", "dataset")

    # Verify result
    expected_result = [
        {
            "id": "resource-1",
            "name": "Resource 1",
            "created_at": created_time.strftime(DATETIME_STRING_FORMAT),
        },
        {
            "id": "resource-2",
            "name": "Resource 2",
            "created_at": created_time.strftime(DATETIME_STRING_FORMAT),
        },
    ]
    assert result == expected_result

    # Verify method call
    mock_resources_client.get_project_resource_records.assert_called_once_with(
        "test-project", "dataset"
    )


def test_list_empty(resource_provider, mock_resources_client):
    """Test listing resources when none exist."""
    # Setup mock response with empty list
    response = MagicMock()
    response.resource_records = []  # Direct assignment for clean mocking
    mock_resources_client.get_project_resource_records.return_value = response

    # Call the method
    result = resource_provider.list("test-project", "dataset")

    # Verify result is empty list
    assert result == []

    # Verify method call
    mock_resources_client.get_project_resource_records.assert_called_once_with(
        "test-project", "dataset"
    )
