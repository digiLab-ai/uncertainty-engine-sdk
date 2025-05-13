import os
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
import requests
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostResourceRecordRequest,
    PostResourceVersionRequest,
    ResourceRecordInput,
    ResourceVersionRecordInput,
)

from uncertainty_engine.api_providers.resource_provider import (
    DATETIME_STRING_FORMAT,
    ResourceProvider,
)

### __init__ ###


def test_init_default(mock_auth_service):
    """Test initializing with default parameters."""

    provider = ResourceProvider(mock_auth_service)

    assert provider.auth_service is mock_auth_service
    assert provider.client is not None
    assert provider.projects_client is not None
    assert provider.resources_client is not None


def test_init_custom(mock_auth_service):
    """Test initializing with custom parameters."""

    custom_url = "http://custom-url.com"

    provider = ResourceProvider(deployment=custom_url, auth_service=mock_auth_service)

    assert provider.auth_service is mock_auth_service
    assert provider.client.configuration.host == custom_url


### resource_provider.account_id ###


def test_account_id_with_auth_service(resource_provider, mock_auth_service):
    """Test the account_id property when auth_service is available."""
    assert resource_provider.account_id == mock_auth_service.account_id


def test_account_id_without_auth_service():
    """Test the account_id property when auth_service is not available."""

    provider = ResourceProvider(auth_service=None)
    assert provider.account_id is None


### resource_provider.upload ###


def test_upload_success(
    resource_provider,
    mock_resources_client,
    mock_file,
    mock_resource_record,
    mock_version_response,
):
    """Test the upload method when successful."""
    # Setup mock responses
    mock_resources_client.post_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

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
    with patch.object(resource_provider, "auth_service", None):
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
    resource_provider, mock_resources_client, mock_resource_record
):
    """Test handling of ApiException during version record creation."""
    # Setup mocks
    mock_resources_client.post_resource_record.return_value = mock_resource_record

    # Setup exception
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.post_resource_version.side_effect = api_exception

    # Call and verify exception
    with pytest.raises(Exception, match="Error creating version record:"):
        resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


@pytest.mark.parametrize(
    "status_code,error_text,expected_error_msg",
    [
        (403, "Forbidden", "Upload failed with status 403: Forbidden"),
        (500, "Server Error", "Upload failed with status 500: Server Error"),
    ],
)
def test_upload_failed_file_upload(
    resource_provider,
    mock_resources_client,
    mock_resource_record,
    mock_version_response,
    mock_file,
    status_code,
    error_text,
    expected_error_msg,
):
    """Test handling of failed upload to presigned URL with various error codes."""
    # Setup mocks
    mock_resources_client.post_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = status_code
    mock_put_response.text = error_text

    with patch("builtins.open", mock_file):
        with patch("requests.put", return_value=mock_put_response):
            # Call and verify exception
            with pytest.raises(Exception, match=expected_error_msg):
                resource_provider.upload(
                    "project-id", "name", "type", "path/to/file.txt"
                )


def test_upload_failed_completion(
    resource_provider,
    mock_resources_client,
    mock_resource_record,
    mock_version_response,
    mock_file,
):
    """Test handling of exception during upload completion."""
    # Setup mocks
    mock_resources_client.post_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

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


### resource_provider.download ###


def test_download_success_with_filepath(
    resource_provider, mock_file, mock_version_response
):
    """Test downloading a resource with a specified filepath."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        mock_version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

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
                requests.get.assert_called_once_with("https://upload-url.com")
                mock_get_response.raise_for_status.assert_called_once()
                mock_file.assert_called_once_with("path/to/download/file.csv", "wb")
                mock_file().write.assert_called_once_with(b"test file content")


def test_download_success_without_filepath(resource_provider, mock_version_response):
    """Test downloading a resource without a specified filepath (return content)."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        mock_version_response
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
        requests.get.assert_called_once_with("https://upload-url.com")
        mock_get_response.raise_for_status.assert_called_once()


def test_download_no_auth(resource_provider):
    """Test download fails when not authenticated."""
    # Set auth provider to None
    with patch.object(resource_provider, "auth_service", None):
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


def test_download_http_error(resource_provider, mock_version_response):
    """Test handling of HTTP error during download."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        mock_version_response
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


def test_download_file_not_found_error(resource_provider, mock_version_response):
    """Test handling of FileNotFoundError when writing to a file."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        mock_version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    # Setup file mock to raise FileNotFoundError
    mock_file = MagicMock()
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


def test_download_other_file_exception(resource_provider, mock_version_response):
    """Test handling of generic exceptions when writing to a file."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version.return_value = (
        mock_version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    # Setup file mock to raise a permission error
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


### resource_provider.update ###


def test_update_success(
    resource_provider,
    mock_resources_client,
    mock_resource_record,
    mock_version_response,
    mock_file,
):
    """Test updating a resource successfully."""
    # Setup mocks for resource info - simulate two existing versions
    mock_resource_record.resource_record.versions = ["v1", "v2"]
    mock_resources_client.get_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

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


def test_update_resource_not_found(
    resource_provider, mock_resources_client, mock_version_response, mock_file
):
    """Test handling when the resource to update is not found."""
    # Setup exception for resource lookup
    api_exception = ApiException(status=404, reason="Not Found")
    mock_resources_client.get_resource_record.side_effect = api_exception
    mock_resources_client.post_resource_version.return_value = mock_version_response

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                with patch(
                    "uncertainty_engine.api_providers.resource_provider.uuid4",
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
    with patch.object(resource_provider, "auth_service", None):
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
    resource_provider, mock_resources_client, mock_resource_record
):
    """Test handling of ApiException during version record creation."""
    # Setup mocks for resource info
    mock_resources_client.get_resource_record.return_value = mock_resource_record

    # Setup exception for version creation
    api_exception = ApiException(status=400, reason="Bad Request")
    mock_resources_client.post_resource_version.side_effect = api_exception

    with patch("os.path.exists", return_value=True):
        # Call and verify exception
        with pytest.raises(Exception, match="Error creating version record:"):
            resource_provider.update(
                "project-id", "type", "resource-id", "path/to/file.txt"
            )


@pytest.mark.parametrize(
    "status_code,error_text,expected_error_msg",
    [
        (403, "Forbidden", "Upload failed with status 403: Forbidden"),
        (500, "Server Error", "Upload failed with status 500: Server Error"),
    ],
)
def test_update_upload_error(
    resource_provider,
    mock_resources_client,
    mock_resource_record,
    mock_version_response,
    mock_file,
    status_code,
    error_text,
    expected_error_msg,
):
    """Test handling of error during upload to presigned URL."""
    # Setup mocks for resource info
    mock_resources_client.get_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = status_code
    mock_put_response.text = error_text

    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_file):
            with patch("requests.put", return_value=mock_put_response):
                # Call and verify exception
                with pytest.raises(Exception, match=expected_error_msg):
                    resource_provider.update(
                        "test-project",
                        "dataset",
                        "test-resource-id",
                        "path/to/updated_file.json",
                    )


def test_update_finalize_error(
    resource_provider,
    mock_resources_client,
    mock_resource_record,
    mock_version_response,
    mock_file,
):
    """Test handling of error during finalization of upload."""
    # Setup mocks for resource info
    mock_resources_client.get_resource_record.return_value = mock_resource_record
    mock_resources_client.post_resource_version.return_value = mock_version_response

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


### resource_provider.list_resources ###


def test_list_resources_success(resource_provider, mock_resources_client):
    """Test listing resources successfully."""
    # Setup mock response
    created_time = datetime.now()

    # Create mock resource records
    record1 = MagicMock()
    record1.id = "resource-1"
    record1.name = "Resource 1"
    record1.created_at = created_time

    record2 = MagicMock()
    record2.id = "resource-2"
    record2.name = "Resource 2"
    record2.created_at = created_time

    # Create response with list of resource records
    response = MagicMock()
    response.resource_records = [record1, record2]
    mock_resources_client.get_project_resource_records.return_value = response

    # Call the method
    result = resource_provider.list_resources("test-project", "dataset")

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


def test_list_resources_empty(resource_provider, mock_resources_client):
    """Test listing resources when none exist."""
    # Setup mock response with empty list
    response = MagicMock()
    response.resource_records = []
    mock_resources_client.get_project_resource_records.return_value = response

    # Call the method
    result = resource_provider.list_resources("test-project", "dataset")

    # Verify result is empty list
    assert result == []

    # Verify method call
    mock_resources_client.get_project_resource_records.assert_called_once_with(
        "test-project", "dataset"
    )
