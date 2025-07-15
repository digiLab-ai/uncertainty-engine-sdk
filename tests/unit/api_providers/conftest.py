from unittest.mock import MagicMock, patch

import pytest
from uncertainty_engine_resource_client.api.project_records_api import ProjectRecordsApi
from uncertainty_engine_resource_client.api.resources_api import ResourcesApi
from uncertainty_engine_resource_client.api.account_records_api import AccountRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration

from uncertainty_engine.auth_service import AuthService


# API provider fixtures
@pytest.fixture
def mock_api_configuration(mock_deployment: str):
    api_configuration = MagicMock()
    api_configuration.host = mock_deployment
    return api_configuration


@pytest.fixture
def mock_api_client(mock_api_configuration: Configuration):
    api_client = MagicMock()
    api_client.configuration = mock_api_configuration
    return api_client


@pytest.fixture
def mock_account_records_api(mock_api_client: ApiClient):
    accounts_api = MagicMock()
    accounts_api.api_client = mock_api_client
    return accounts_api


@pytest.fixture
def mock_project_records_api(mock_api_client: ApiClient):
    project_records_api = MagicMock()
    project_records_api.api_client = mock_api_client
    return project_records_api


@pytest.fixture
def mock_resources_api(mock_api_client: ApiClient):
    resources_api = MagicMock(spec=AccountRecordsApi)
    resources_api.api_client = mock_api_client
    return resources_api


@pytest.fixture
def mocked_api_clients(
    mock_api_client: ApiClient,
    mock_account_records_api: AccountRecordsApi,
    mock_project_records_api: ProjectRecordsApi,
    mock_resources_api: ResourcesApi,
):
    """Sets up mocked API clients for Provider initialization."""
    api_client_patch = patch(
        "uncertainty_engine_resource_client.api_client.ApiClient",
        return_value=mock_api_client,
    )
    account_records_api_patch = patch(
        "uncertainty_engine_resource_client.api.account_records_api.AccountRecordsApi",
        return_value=mock_account_records_api,
    )
    project_records_api_patch = patch(
        "uncertainty_engine_resource_client.api.project_records_api.ProjectRecordsApi",
        return_value=mock_project_records_api,
    )
    resources_api_patch = patch(
        "uncertainty_engine_resource_client.api.resources_api.ResourcesApi",
        return_value=mock_resources_api,
    )

    with (
        api_client_patch
    ), project_records_api_patch, resources_api_patch, account_records_api_patch:
        yield


@pytest.fixture
def resource_provider(
    mock_auth_service: AuthService, mocked_api_clients, mock_deployment: str
):
    """Creates a ResourceProvider with mocked dependencies."""
    from uncertainty_engine.api_providers.resource_provider import ResourceProvider

    resource_provider = ResourceProvider(mock_auth_service, mock_deployment)
    return resource_provider


@pytest.fixture
def mock_resource_record():
    """Creates a mock resource record."""

    record = MagicMock()
    record.id = "test-resource-id"
    record.name = "Test Resource"
    record.versions = ["v1"]

    response = MagicMock()
    response.resource_record = record
    return response


@pytest.fixture
def mock_version_response():
    """Creates a mock version response."""
    response = MagicMock()
    response.url = "https://upload-url.com"
    response.pending_record_id = "test-pending-id"
    return response
