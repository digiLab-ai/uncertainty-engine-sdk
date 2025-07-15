from typing import Any, Iterator

import pytest
from uncertainty_engine_resource_client.api import AccountRecordsApi, ProjectRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient

from uncertainty_engine.api_providers import ProjectsProvider
from uncertainty_engine.auth_service import AuthService


@pytest.fixture
def projects_provider(
    mock_auth_service: AuthService,
    mock_deployment: str,
    mocked_api_clients: Iterator[Any],
):
    """Creates a ProjectsProvider with mocked dependencies."""
    from uncertainty_engine.api_providers.projects_provider import ProjectsProvider

    projects_provider = ProjectsProvider(mock_auth_service, mock_deployment)
    return projects_provider


# ProjectsProvider Init Tests
def test_init_creates_clients(
    projects_provider: ProjectsProvider,
):
    """Test that initialization creates record and version managers."""
    assert hasattr(projects_provider, "client")
    assert hasattr(projects_provider, "accounts_client")
    assert hasattr(projects_provider, "projects_client")
    assert isinstance(projects_provider.client, ApiClient)
    assert isinstance(projects_provider.accounts_client, AccountRecordsApi)
    assert isinstance(projects_provider.projects_client, ProjectRecordsApi)


def test_account_id_property(
    projects_provider: ProjectsProvider,
    mock_account_id: str,
    mock_auth_service: AuthService,
):
    """Test account_id property returns auth service account_id."""
    assert projects_provider.account_id == mock_account_id

    mock_auth_service.account_id = None
    assert projects_provider.account_id is None


def test_update_api_authentication(
    projects_provider: ProjectsProvider, mock_auth_service: AuthService
):
    """Test API authentication headers are updated correctly."""
    # Test authenticated state
    mock_auth_service.get_auth_header.reset_mock()
    mock_auth_service.is_authenticated = True
    projects_provider.update_api_authentication()
    mock_auth_service.get_auth_header.assert_called_once()

    # Test unauthenticated state
    mock_auth_service.get_auth_header.reset_mock()
    mock_auth_service.is_authenticated = False
    projects_provider.update_api_authentication()
    mock_auth_service.get_auth_header.assert_not_called()
