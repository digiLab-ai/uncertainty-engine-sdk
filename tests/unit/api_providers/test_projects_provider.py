from datetime import datetime
from typing import Any, Iterator
from unittest.mock import MagicMock

import pytest
from uncertainty_engine_resource_client.api import AccountRecordsApi, ProjectRecordsApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import ProjectRecordOutput

from uncertainty_engine.api_providers import ProjectsProvider
from uncertainty_engine.api_providers.constants import DATETIME_STRING_FORMAT
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


@pytest.fixture
def mock_project_record() -> ProjectRecordOutput:
    mock_record = MagicMock(spec=ProjectRecordOutput)
    mock_record.id = "project-123"
    mock_record.name = "Test Project"
    mock_record.owner_id = "owner-123"
    mock_record.created_at = datetime(2024, 1, 1, 12, 0, 0)
    return mock_record


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


# ProjectsProvider list_projects tests
def test_list_projects_success(
    projects_provider: ProjectsProvider,
    mock_project_record: ProjectRecordOutput,
):
    """Test successful projects listing."""
    mock_response = MagicMock()
    mock_response.project_records = [mock_project_record]
    projects_provider.accounts_client.get_account_record_projects = MagicMock(
        return_value=mock_response
    )

    result = projects_provider.list_projects()

    # Verify the result
    assert len(result) == 1
    assert result[0].id == mock_project_record.id
    assert result[0].name == mock_project_record.name
    assert result[0].created_at == mock_project_record.created_at.strftime(
        DATETIME_STRING_FORMAT
    )

    projects_provider.accounts_client.get_account_record_projects.assert_called_once_with(
        projects_provider.account_id
    )


def test_list_projects_api_exception(projects_provider: ProjectsProvider):
    """Test handling of API exceptions during listing."""
    projects_provider.accounts_client.get_account_record_projects = MagicMock(
        side_effect=ApiException(status=404, reason="Not Found")
    )

    with pytest.raises(Exception, match="Failed to fetch project records"):
        projects_provider.list_projects()


def test_list_projects_validation_error(projects_provider: ProjectsProvider):
    """Tests handling of validation errors during listing"""
    mock_response = MagicMock()
    mock_response.project_records = [{"invalid": "data"}]

    projects_provider.accounts_client.get_account_record_projects = MagicMock(
        return_value=mock_response
    )

    with pytest.raises(Exception, match="Error listing project records"):
        projects_provider.list_projects()
