from unittest.mock import MagicMock, mock_open, patch

import pytest
from uncertainty_engine_resource_client.api import ProjectRecordsApi, ResourcesApi

from uncertainty_engine.api_providers.resource_provider import ResourceProvider


@pytest.fixture
def mock_auth_service():
    """Fixture for a mock authentication provider."""
    auth_service = MagicMock()
    auth_service.account_id = "test-account-id"
    return auth_service


@pytest.fixture
def mock_projects_client():
    """Fixture for a mock projects client."""
    return MagicMock()


@pytest.fixture
def mock_resources_client():
    """Fixture for a mock resources client."""
    return MagicMock()


@pytest.fixture
def patched_api_classes():
    """Patch all API-related classes."""
    with patch(
        "uncertainty_engine_resource_client.api_client.ApiClient"
    ) as patched_api_client:
        with patch.object(
            ProjectRecordsApi, "__init__", return_value=None
        ) as patched_project_api:
            with patch.object(
                ResourcesApi, "__init__", return_value=None
            ) as patched_resource_api:
                yield {
                    "api_client": patched_api_client,
                    "project_api": patched_project_api,
                    "resource_api": patched_resource_api,
                }


@pytest.fixture
def resource_provider(
    mock_auth_service, mock_projects_client, mock_resources_client, patched_api_classes
):
    """Create a ResourceProvider with mocked dependencies."""
    provider = ResourceProvider(auth_service=mock_auth_service)
    provider.projects_client = mock_projects_client
    provider.resources_client = mock_resources_client
    return provider


@pytest.fixture
def mock_file_content():
    """Default mock file content."""
    return b"test file content"


@pytest.fixture
def mock_file(mock_file_content):
    """Mock the open function for file operations."""
    return mock_open(read_data=mock_file_content)


@pytest.fixture
def mock_resource_record(
    resource_id="test-resource-id", name="Test Resource", versions=None
):
    """Create a mock resource record."""
    if versions is None:
        versions = ["v1"]

    record = MagicMock()
    record.id = resource_id
    record.name = name
    record.versions = versions

    response = MagicMock()
    response.resource_record = record
    return response


@pytest.fixture
def mock_version_response(url="https://upload-url.com", pending_id="test-pending-id"):
    """Create a mock version response."""
    response = MagicMock()
    response.url = url
    response.pending_record_id = pending_id
    return response
