from unittest.mock import MagicMock, patch

import pytest


# API provider fixtures
@pytest.fixture
def mock_api_configuration(mock_deployment):
    api_configuration = MagicMock()
    api_configuration.host = mock_deployment
    return api_configuration


@pytest.fixture
def mock_api_client(mock_api_configuration):
    api_client = MagicMock()
    api_client.configuration = mock_api_configuration
    return api_client


@pytest.fixture
def mock_project_records_api(mock_api_client):
    project_records_api = MagicMock()
    project_records_api.api_client = mock_api_client
    return project_records_api


@pytest.fixture
def mock_resources_api(mock_api_client):
    resources_api = MagicMock()
    resources_api.api_client = mock_api_client
    return resources_api


@pytest.fixture
def mocked_api_clients(mock_api_client, mock_project_records_api, mock_resources_api):
    """Sets up mocked API clients for ResourceProvider initialization."""
    api_client_patch = patch(
        "uncertainty_engine_resource_client.api_client.ApiClient",
        return_value=mock_api_client,
    )
    project_records_api_patch = patch(
        "uncertainty_engine_resource_client.api.project_records_api.ProjectRecordsApi",
        return_value=mock_project_records_api,
    )
    resources_api_patch = patch(
        "uncertainty_engine_resource_client.api.resources_api.ResourcesApi",
        return_value=mock_resources_api,
    )

    with api_client_patch, project_records_api_patch, resources_api_patch:
        yield


@pytest.fixture
def resource_provider(mock_auth_service, mocked_api_clients, mock_deployment):
    """Creates a ResourceProvider with mocked dependencies."""
    from uncertainty_engine.api_providers.resource_provider import ResourceProvider

    resource_provider = ResourceProvider(mock_auth_service, mock_deployment)
    return resource_provider


@pytest.fixture
def mock_resource_record(
    resource_id="test-resource-id", name="Test Resource", versions=None
):
    """Creates a mock resource record."""
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
    """Creates a mock version response."""
    response = MagicMock()
    response.url = url
    response.pending_record_id = pending_id
    return response
