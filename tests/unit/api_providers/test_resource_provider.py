import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostResourceRecordRequest,
    PostResourceVersionRequest,
    ResourceRecordInput,
    ResourceRecordOutput,
    ResourceVersionRecordInput,
)

from uncertainty_engine.api_providers import ResourceProvider
from uncertainty_engine.auth_service import AuthService


def test_init_default(mock_auth_service: AuthService):
    """Test initializing with default parameters."""

    provider = ResourceProvider(mock_auth_service)

    assert provider.auth_service is mock_auth_service
    assert provider.client is not None
    assert provider.projects_client is not None
    assert provider.resources_client is not None


def test_init_custom(
    mock_auth_service: AuthService,
):
    """Test initializing with custom parameters."""

    custom_url = "http://custom-url.com"

    provider = ResourceProvider(deployment=custom_url, auth_service=mock_auth_service)

    assert provider.auth_service is mock_auth_service
    assert provider.client.configuration.host == custom_url


def test_account_id_when_authenticated(
    resource_provider: ResourceProvider, mock_auth_service: AuthService
):
    # Set up the mock auth service to return an account_id
    mock_auth_service.account_id = "test-user-123"

    # Test that the resource provider gets the correct account_id
    assert resource_provider.account_id == "test-user-123"


def test_account_id_when_not_authenticated(
    resource_provider: ResourceProvider, mock_auth_service: AuthService
):
    # Set up the mock auth service to return None (not authenticated)
    mock_auth_service.account_id = None

    # Test that the resource provider correctly returns None
    assert resource_provider.account_id is None


def test_upload_success(
    resource_provider: ResourceProvider,
    mock_file: MagicMock,
    mock_resource_record: MagicMock,
    mock_version_response: ResourceProvider,
):
    """Test the upload method when successful."""
    # Setup mock responses
    resource_provider.resources_client.post_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )
    resource_provider.resources_client.put_upload_resource_version = MagicMock(
        return_value=None
    )

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Test parameters
    project_id = "test-project"
    name = "Test Resource"
    resource_type = "dataset"
    file_path = "path/to/test_file.csv"

    with patch("requests.put", return_value=mock_put_response) as mock_requests_put:
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
        resource_provider.resources_client.post_resource_record.assert_called_once_with(
            project_id,
            resource_type,
            PostResourceRecordRequest(
                resource_record=ResourceRecordInput(
                    name=name, owner_id=resource_provider.account_id
                )
            ),
        )

        resource_provider.resources_client.post_resource_version.assert_called_once_with(
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
        mock_requests_put.assert_called_once_with(
            "https://upload-url.com", data=mock_file()
        )

        resource_provider.resources_client.put_upload_resource_version.assert_called_once_with(
            project_id, resource_type, "test-resource-id", "test-pending-id"
        )


def test_upload_no_auth(resource_provider: ResourceProvider):
    """Test upload fails when not authenticated."""

    # Set auth provider authentication to None
    resource_provider.auth_service = MagicMock(
        is_authenticated=False, account_id=None, token=None
    )

    with pytest.raises(
        ValueError, match="Authentication required before uploading resources"
    ):
        resource_provider.upload("project-id", "name", "type", "path")


def test_upload_api_exception_on_record_creation(resource_provider: ResourceProvider):
    """Test handling of ApiException during resource record creation."""
    # Setup mock error
    api_exception = ApiException(status=400, reason="Bad Request")
    resource_provider.resources_client.post_resource_record = MagicMock(
        side_effect=api_exception
    )

    # Call and verify exception
    with pytest.raises(Exception, match="Error creating resource record:"):
        resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


def test_upload_api_exception_on_version_creation(
    resource_provider: ResourceProvider, mock_resource_record: MagicMock
):
    """Test handling of ApiException during version record creation."""
    resource_provider.resources_client.post_resource_record = MagicMock(
        return_value=mock_resource_record
    )

    # Setup exception
    api_exception = ApiException(status=400, reason="Bad Request")
    resource_provider.resources_client.post_resource_version = MagicMock(
        side_effect=api_exception
    )

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
def test_upload_file_upload_error(
    resource_provider: ResourceProvider,
    mock_resource_record: MagicMock,
    mock_version_response: MagicMock,
    mock_file: MagicMock,
    status_code: int,
    error_text: str,
    expected_error_msg: str,
):
    """Test handling of failed upload to presigned URL with various error codes."""
    # Setup mocks
    resource_provider.resources_client.post_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = status_code
    mock_put_response.text = error_text

    with patch("requests.put", return_value=mock_put_response):
        # Call and verify exception
        with pytest.raises(Exception, match=expected_error_msg):
            resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


def test_upload_failed_completion(
    resource_provider: ResourceProvider,
    mock_resource_record: MagicMock,
    mock_version_response: MagicMock,
    mock_file: MagicMock,
):
    """Test handling of exception during upload completion."""
    # Setup mocks
    resource_provider.resources_client.post_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Setup exception on completion
    api_exception = ApiException(status=400, reason="Bad Request")
    resource_provider.resources_client.put_upload_resource_version = MagicMock(
        side_effect=api_exception
    )

    with patch("requests.put", return_value=mock_put_response):
        # Call and verify exception
        with pytest.raises(Exception, match="Error completing upload:"):
            resource_provider.upload("project-id", "name", "type", "path/to/file.txt")


def test_download_success_with_filepath(
    resource_provider: ResourceProvider,
    mock_file: MagicMock,
    mock_version_response: MagicMock,
):
    """Test downloading a resource with a specified filepath."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version = MagicMock(
        return_value=mock_version_response
    )

    # Setup requests mock
    mock_get_response = MagicMock()
    mock_get_response.content = b"test file content"

    with patch("os.makedirs") as mock_makedirs, patch(
        "requests.get", return_value=mock_get_response
    ):
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


def test_download_success_without_filepath(
    resource_provider: ResourceProvider, mock_version_response: MagicMock
):
    """Test downloading a resource without a specified filepath (return content)."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version = MagicMock(
        return_value=mock_version_response
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


def test_download_no_auth(resource_provider: ResourceProvider):
    """Test download fails when not authenticated."""

    # Set auth provider authentication to None
    resource_provider.auth_service = MagicMock(
        is_authenticated=False, account_id=None, token=None
    )

    # Call and verify exception
    with pytest.raises(
        ValueError, match="Authentication required before downloading resources"
    ):
        resource_provider.download("project-id", "type", "resource-id")


def test_download_api_exception(resource_provider: ResourceProvider):
    """Test handling of ApiException during resource version retrieval."""
    # Setup exception
    api_exception = ApiException(status=404, reason="Not Found")
    resource_provider.resources_client.get_latest_resource_version = MagicMock(
        side_effect=api_exception
    )

    # Call and verify exception
    with pytest.raises(Exception, match="Error retrieving resource:"):
        resource_provider.download(
            "project-id", "type", "resource-id", "path/to/file.txt"
        )


def test_download_generic_exception_on_retrieval(resource_provider: ResourceProvider):
    """Test handling of generic Exception during resource retrieval."""
    # Setup exception
    generic_exception = Exception("Random error")
    resource_provider.resources_client.get_latest_resource_version = MagicMock(
        side_effect=generic_exception
    )

    # Call and verify exception
    with pytest.raises(Exception, match="Error retrieving resource: Random error"):
        resource_provider.download(
            "project-id", "type", "resource-id", "path/to/file.txt"
        )


def test_download_http_error(
    resource_provider: ResourceProvider, mock_version_response: MagicMock
):
    """Test handling of HTTP error during download."""
    # Setup mocks
    resource_provider.resources_client.get_latest_resource_version = MagicMock(
        return_value=mock_version_response
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


def test_update_success(
    resource_provider: ResourceProvider,
    mock_resource_record: MagicMock,
    mock_version_response: MagicMock,
    mock_file: MagicMock,
):
    """Test updating a resource successfully."""
    # Setup mocks for resource info - simulate two existing versions
    mock_resource_record.resource_record.versions = ["v1", "v2"]
    resource_provider.resources_client.get_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )
    resource_provider.resources_client.put_upload_resource_version = MagicMock(
        return_value=None
    )

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    with patch("os.path.exists", return_value=True):
        with patch("requests.put", return_value=mock_put_response):
            # Call the method
            resource_provider.update(
                project_id="test-project",
                resource_type="dataset",
                resource_id="test-resource-id",
                file_path="path/to/updated_file.json",
            )

            # Verify method calls
            resource_provider.resources_client.get_resource_record.assert_called_once_with(
                "test-project", "dataset", "test-resource-id"
            )

            # Expected version name should be resource name + v3 (since there are two existing versions)
            resource_provider.resources_client.post_resource_version.assert_called_once_with(
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

            resource_provider.resources_client.put_upload_resource_version.assert_called_once_with(
                "test-project", "dataset", "test-resource-id", "test-pending-id"
            )


def test_update_resource_not_found(
    resource_provider: ResourceProvider,
    mock_version_response: ResourceProvider,
    mock_file: ResourceProvider,
):
    """Test handling when the resource to update is not found."""
    # Setup exception for resource lookup

    resource_provider.get_resource_record = MagicMock(
        side_effect=ApiException(status=404, reason="Not Found")
    )
    resource_provider.post_resource_version = MagicMock(
        return_value=mock_version_response
    )
    resource_provider.resources_client.put_upload_resource_version = MagicMock(
        return_value=None
    )

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    with patch("os.path.exists", return_value=True):
        with patch("requests.put", return_value=mock_put_response):
            with pytest.raises(
                Exception,
                match="Unable to retrieve resource record. Please ensure the resource exists before attempting to update it.",
            ):
                resource_provider.update(
                    project_id="test-project",
                    resource_type="dataset",
                    resource_id="test-resource-id",
                    file_path="path/to/updated_file.json",
                )


def test_update_no_auth(resource_provider: ResourceProvider):
    """Test update fails when not authenticated."""
    # Set auth provider authentication to None
    resource_provider.auth_service = MagicMock(
        is_authenticated=False, account_id=None, token=None
    )

    # Call and verify exception
    with pytest.raises(
        ValueError, match="Authentication required before updating resources"
    ):
        resource_provider.update(
            "project-id", "type", "resource-id", "path/to/file.txt"
        )


def test_update_file_not_found(resource_provider: ResourceProvider):
    """Test update fails when the file doesn't exist."""
    with patch("os.path.exists", return_value=False):
        # Call and verify exception
        with pytest.raises(FileNotFoundError, match="File not found:"):
            resource_provider.update(
                "project-id", "type", "resource-id", "nonexistent/file.txt"
            )


def test_update_api_exception_on_version_creation(
    resource_provider: ResourceProvider, mock_resource_record: MagicMock
):
    """Test handling of ApiException during version record creation."""
    # Setup mocks for resource info
    resource_provider.get_resource_record = MagicMock(return_value=mock_resource_record)

    # Setup exception for version creation
    api_exception = ApiException(status=400, reason="Bad Request")
    resource_provider.post_resource_version = MagicMock(side_effect=api_exception)

    with patch("os.path.exists", return_value=True):
        # Call and verify exception
        with pytest.raises(
            Exception,
            match="Unable to retrieve resource record. Please ensure the resource exists before attempting to update it.",
        ):
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
    resource_provider: ResourceProvider,
    mock_resource_record: MagicMock,
    mock_version_response: MagicMock,
    mock_file: MagicMock,
    status_code: str,
    error_text: str,
    expected_error_msg: str,
):
    """Test handling of error during upload to presigned URL."""
    # Setup mocks for resource info
    resource_provider.resources_client.get_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )

    # Setup requests mock with error
    mock_put_response = MagicMock()
    mock_put_response.status_code = status_code
    mock_put_response.text = error_text

    with patch("os.path.exists", return_value=True):
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
    resource_provider: ResourceProvider,
    mock_resource_record: MagicMock,
    mock_version_response: MagicMock,
    mock_file: MagicMock,
):
    """Test handling of error during finalization of upload."""
    # Setup mocks for resource info
    resource_provider.resources_client.get_resource_record = MagicMock(
        return_value=mock_resource_record
    )
    resource_provider.resources_client.post_resource_version = MagicMock(
        return_value=mock_version_response
    )

    # Setup requests mock
    mock_put_response = MagicMock()
    mock_put_response.status_code = 200

    # Setup exception for finalization
    api_exception = ApiException(status=400, reason="Bad Request")
    resource_provider.put_upload_resource_version = MagicMock(side_effect=api_exception)

    with patch("os.path.exists", return_value=True):
        with patch("requests.put", return_value=mock_put_response):
            # Call and verify exception
            with pytest.raises(Exception, match="Error finalizing upload:"):
                resource_provider.update(
                    "test-project",
                    "dataset",
                    "test-resource-id",
                    "path/to/updated_file.json",
                )


def test_list_resources_success(
    resource_provider: ResourceProvider, mock_resource_record: ResourceRecordOutput
):
    """Test listing resources successfully."""
    record = mock_resource_record.resource_record
    response = MagicMock()
    response.resource_records = [record]

    resource_provider.resources_client.get_project_resource_records = MagicMock(
        return_value=response
    )

    # Call the method
    result = resource_provider.list_resources("test-project", "dataset")

    # Verify result
    expected_result = [mock_resource_record.resource_record]
    assert result == expected_result


def test_list_resources_validation_error(resource_provider: ResourceProvider):
    """Tests handling of validation errors during listing"""
    mock_response = MagicMock()
    mock_response.resource_records = [{"invalid": "data"}]

    resource_provider.resources_client.get_project_resource_records = MagicMock(
        return_value=mock_response
    )

    with pytest.raises(Exception, match="Error listing project resources"):
        resource_provider.list_resources("test-project", "dataset")


def test_list_resources_empty(resource_provider: ResourceProvider):
    """Test listing resources when none exist."""
    # Setup mock response with empty list
    response = MagicMock()
    response.resource_records = []
    resource_provider.resources_client.get_project_resource_records = MagicMock(
        return_value=response
    )

    # Call the method
    result = resource_provider.list_resources("test-project", "dataset")

    # Verify result is empty list
    assert result == []

    # Verify method call
    resource_provider.resources_client.get_project_resource_records.assert_called_once_with(
        "test-project", "dataset"
    )


def test_delete_resource_success(
    resource_provider: ResourceProvider, caplog: pytest.LogCaptureFixture
):
    """Test deleting a resource successfully."""
    # Setup mock response
    resource_provider.resources_client.delete_resource_record = MagicMock()

    with caplog.at_level("INFO"):
        # Call the method
        resource_provider.delete_resource("test-project", "dataset", "test-resource-id")

    # Verify method calls
    resource_provider.resources_client.delete_resource_record.assert_called_once_with(
        "test-project", "dataset", "test-resource-id"
    )

    # Verify output
    assert any(
        record.levelname == "INFO"
        and record.getMessage()
        == "Resource test-resource-id deleted successfully from project test-project."
        for record in caplog.records
    )


def test_delete_generic_exception(resource_provider: ResourceProvider):
    """Test handling of generic exception during resource deletion."""
    # Setup exception
    resource_provider.resources_client.delete_resource_record = MagicMock(
        side_effect=ValueError("Random error")
    )

    # Call and verify exception
    with pytest.raises(Exception) as exc_info:
        resource_provider.delete_resource("test-project", "dataset", "test-resource-id")

    # Verify output
    assert str(exc_info.value) == "Error deleting resource: Random error"


def test_delete_api_exception(resource_provider: ResourceProvider):
    """Test handling of ApiException during resource deletion."""
    # Setup exception
    api_exception = ApiException(status=404, reason="Not Found")
    resource_provider.resources_client.delete_resource_record = MagicMock(
        side_effect=api_exception
    )

    # Call and verify exception
    with pytest.raises(
        Exception, match="Error deleting resource: API Error: Not Found"
    ):
        resource_provider.delete_resource("test-project", "dataset", "test-resource-id")
