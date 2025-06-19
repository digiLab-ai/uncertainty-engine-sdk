from datetime import datetime
from unittest.mock import Mock

import pytest
from pytest import MonkeyPatch
from uncertainty_engine_resource_client.api import WorkflowsApi
from uncertainty_engine_resource_client.exceptions import ApiException
from uncertainty_engine_resource_client.models import (
    PostWorkflowRecordRequest,
    PostWorkflowVersionRequest,
    WorkflowRecordOutput,
    WorkflowVersionRecordOutput,
)

from uncertainty_engine.api_providers.workflows_provider import (
    RecordManager,
    VersionManager,
    WorkflowsProvider,
)
from uncertainty_engine.api_providers.models import WorkflowRecord, WorkflowVersion
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.nodes.workflow import Workflow


# Fixtures
@pytest.fixture
def unauthenticated_auth_service():
    """Mock unauthenticated service."""
    auth_service = Mock(spec=AuthService)
    auth_service.is_authenticated = False
    auth_service.account_id = None
    auth_service.get_auth_header.return_value = {}
    return auth_service


@pytest.fixture
def mock_workflow():
    """Mock workflow object."""
    workflow = Mock(spec=Workflow)
    workflow.__dict__ = {
        "graph": {"nodes": [], "edges": []},
        "inputs": {"input1": "value1"},
        "requested_output": "output1",
        "external_input_id": "external-123",
    }
    return workflow


@pytest.fixture
def workflows_provider(
    mock_auth_service: AuthService, mocked_api_clients: None, mock_deployment: str
):
    """Creates a WorkflowsProvider with mocked dependencies."""
    from uncertainty_engine.api_providers.workflows_provider import WorkflowsProvider

    workflows_provider = WorkflowsProvider(mock_auth_service, mock_deployment)
    return workflows_provider


@pytest.fixture
def mock_workflows_client():
    """Mock workflows API client."""
    return Mock()


@pytest.fixture
def record_manager(mock_workflows_client: WorkflowsApi, mock_auth_service: AuthService):
    """Create RecordManager instance."""
    return RecordManager(mock_workflows_client, mock_auth_service)


@pytest.fixture
def version_manager(
    mock_workflows_client: WorkflowsApi, mock_auth_service: AuthService
):
    """Create VersionManager instance."""
    return VersionManager(mock_workflows_client, mock_auth_service)


# WorkflowsProvider Init Tests
def test_init_creates_managers(
    mock_auth_service: AuthService, mocked_api_clients: None
):
    """Test that initialization creates record and version managers."""
    provider = WorkflowsProvider(mock_auth_service)

    assert hasattr(provider, "_record_manager")
    assert hasattr(provider, "_version_manager")
    assert isinstance(provider._record_manager, RecordManager)
    assert isinstance(provider._version_manager, VersionManager)


def test_account_id_property(
    workflows_provider: WorkflowsProvider, mock_auth_service: AuthService
):
    """Test account_id property returns auth service account_id."""
    assert workflows_provider.account_id == "mock_account_id"

    mock_auth_service.account_id = None
    assert workflows_provider.account_id is None


def test_list_workflows_success(workflows_provider: WorkflowsProvider):
    """Test successful workflow listing."""
    # Mock workflow records
    mock_record = Mock(spec=WorkflowRecordOutput)
    mock_record.id = "workflow-123"
    mock_record.name = "Test Workflow"
    mock_record.owner_id = "mock_account_id"
    mock_record.created_at = datetime(2024, 1, 1, 12, 0, 0)
    mock_record.versions = ["version-1", "version-2", "version-3"]

    workflows_provider._record_manager.list_records = Mock(return_value=[mock_record])

    result = workflows_provider.list_workflows("project-123")

    expected = [
        WorkflowRecord(
            id="workflow-123",
            name="Test Workflow",
            owner_id="mock_account_id",
            created_at="12:00:00 2024-01-01",
            versions=["version-1", "version-2", "version-3"],
        )
    ]

    assert result == expected
    workflows_provider._record_manager.list_records.assert_called_once_with(
        "project-123"
    )


def test_list_workflow_versions(
    workflows_provider: WorkflowsProvider, mock_workflow: Workflow
):
    """Test listing workflow versions."""
    mock_version = Mock(spec=WorkflowVersionRecordOutput)
    mock_version.id = "version-123"
    mock_version.name = "version"
    mock_version.owner_id = "mock_account_id"
    mock_version.created_at = datetime(2024, 1, 1, 12, 0, 0)

    workflows_provider._version_manager.list_versions = Mock(
        return_value=[mock_version]
    )

    result = workflows_provider.list_workflow_versions("project-123", "workflow-123")

    expected = [
        WorkflowVersion(
            id="version-123",
            name="version",
            created_at="12:00:00 2024-01-01",
            owner_id="mock_account_id",
        )
    ]

    assert result == expected
    workflows_provider._version_manager.list_versions.assert_called_once_with(
        "project-123", "workflow-123"
    )


def test_load_workflow_success(
    workflows_provider: WorkflowsProvider, mock_workflow: Workflow
):
    """Test successful workflow loading."""
    workflows_provider._version_manager.read_version = Mock(return_value=mock_workflow)

    result = workflows_provider.load("project-123", "workflow-123", "version-456")

    assert result == mock_workflow
    workflows_provider._version_manager.read_version.assert_called_once_with(
        "project-123", "workflow-123", "version-456"
    )


def test_save_workflow_new(
    workflows_provider: WorkflowsProvider, mock_workflow: Workflow
):
    """Test saving a new workflow (no workflow_id provided)."""
    workflows_provider._record_manager.create_record = Mock(return_value="workflow-123")
    workflows_provider._version_manager.create_version = Mock(
        return_value="version-456"
    )
    result = workflows_provider.save(
        "project-123", mock_workflow, workflow_name="New Workflow"
    )

    assert result == "workflow-123"
    workflows_provider._record_manager.create_record.assert_called_once_with(
        "project-123", "New Workflow"
    )
    workflows_provider._version_manager.create_version.assert_called_once_with(
        "project-123", "workflow-123", mock_workflow
    )


def test_save_workflow_existing(
    workflows_provider: WorkflowsProvider, mock_workflow: Workflow
):
    """Test saving to existing workflow (workflow_id provided)."""
    workflows_provider._version_manager.create_version = Mock(
        return_value="version-456"
    )
    workflows_provider._record_manager.create_record = Mock()  # Mock explicitly

    result = workflows_provider.save(
        "project-123", mock_workflow, workflow_id="workflow-123"
    )

    assert result == "workflow-123"
    workflows_provider._record_manager.create_record.assert_not_called()
    workflows_provider._version_manager.create_version.assert_called_once_with(
        "project-123", "workflow-123", mock_workflow
    )


def test_save_workflow_new_no_name(
    workflows_provider: WorkflowsProvider, mock_workflow: Workflow
):
    """Test saving a new workflow without a name."""
    with pytest.raises(
        ValueError, match="workflow_name must be provided to create a new workflow."
    ):
        workflows_provider.save("project-123", mock_workflow)


@pytest.mark.parametrize(
    "method_name,args",
    [
        ("list_workflows", ("project-123",)),
        ("list_workflow_versions", ("project-123", "workflow-123")),
        ("load", ("project-123", "workflow-123")),
        ("save", ("project-123", "Test Workflow", "mock_workflow")),
    ],
    ids=[
        "list_workflows",
        "list_workflow_versions",
        "load",
        "save",
    ],
)
def test_methods_no_auth(
    workflows_provider: WorkflowsProvider,
    mock_auth_service: AuthService,
    mock_workflow: Workflow,
    method_name: str,
    args: tuple[str, ...],
):
    """Test that all methods throw ValueError when no authentication is provided."""
    mock_auth_service.account_id = None

    # Replace "mock_workflow" string with the actual mock object
    processed_args = [mock_workflow if arg == "mock_workflow" else arg for arg in args]
    method = getattr(workflows_provider, method_name)

    with pytest.raises(ValueError, match="Authentication required"):
        method(*processed_args)


# RecordManager Tests
def test_create_record_success(
    record_manager: RecordManager, mock_workflows_client: WorkflowsApi
):
    """Test successful record creation."""
    # Mock API response
    mock_response = Mock()
    mock_response.workflow_record.id = "workflow-123"
    mock_workflows_client.post_workflow_record = Mock(return_value=mock_response)

    result = record_manager.create_record("project-123", "Test Workflow")

    assert result == "workflow-123"
    mock_workflows_client.post_workflow_record.assert_called_once()

    # Verify the request was constructed correctly
    call_args = mock_workflows_client.post_workflow_record.call_args
    project_id, request_body = call_args[0]

    assert project_id == "project-123"
    assert isinstance(request_body, PostWorkflowRecordRequest)
    assert request_body.workflow_record.name == "Test Workflow"
    assert request_body.workflow_record.owner_id == "mock_account_id"


def test_create_record_no_id_returned(
    record_manager: RecordManager, mock_workflows_client: WorkflowsApi
):
    """Test error when no workflow ID is returned."""
    mock_response = Mock()
    mock_response.workflow_record.id = None
    mock_workflows_client.post_workflow_record = Mock(return_value=mock_response)

    with pytest.raises(Exception, match="Error creating workflow record"):
        record_manager.create_record("project-123", "Test Workflow")


def test_create_record_api_exception(
    record_manager: RecordManager, mock_workflows_client: WorkflowsApi
):
    """Test handling of API exceptions."""
    mock_workflows_client.post_workflow_record = Mock(
        side_effect=ApiException(status=400, reason="Bad Request")
    )

    with pytest.raises(Exception, match="Error creating workflow record"):
        record_manager.create_record("project-123", "Test Workflow")


def test_list_records_success(
    record_manager: RecordManager, mock_workflows_client: WorkflowsApi
):
    """Test successful record listing."""
    mock_record = Mock(spec=WorkflowRecordOutput)
    mock_response = Mock()
    mock_response.workflow_records = [mock_record]
    mock_workflows_client.get_project_workflow_records = Mock(
        return_value=mock_response
    )

    result = record_manager.list_records("project-123")

    assert result == [mock_record]
    mock_workflows_client.get_project_workflow_records.assert_called_once_with(
        "project-123"
    )


def test_list_records_api_exception(
    record_manager: RecordManager, mock_workflows_client: WorkflowsApi
):
    """Test handling of API exceptions during listing."""
    mock_workflows_client.get_project_workflow_records = Mock(
        side_effect=ApiException(status=404, reason="Not Found")
    )

    with pytest.raises(Exception, match="Error reading workflow records"):
        record_manager.list_records("project-123")


# VersionManager Tests
def test_create_version_success(
    version_manager: VersionManager,
    mock_workflows_client: WorkflowsApi,
    mock_workflow: Workflow,
):
    """Test successful version creation."""
    # Mock list_versions to return empty list (first version)
    version_manager.list_versions = Mock(return_value=[])

    # Mock API response
    mock_response = Mock()
    mock_response.workflow_version_record.id = "version-456"
    mock_workflows_client.post_workflow_version = Mock(return_value=mock_response)

    result = version_manager.create_version(
        "project-123", "workflow-123", mock_workflow
    )

    assert result == "version-456"
    mock_workflows_client.post_workflow_version.assert_called_once()

    # Verify the request was constructed correctly
    call_args = mock_workflows_client.post_workflow_version.call_args
    project_id, workflow_id, request_body = call_args[0]

    assert project_id == "project-123"
    assert workflow_id == "workflow-123"
    assert isinstance(request_body, PostWorkflowVersionRequest)
    assert request_body.workflow_version_record.name == "version-1"
    assert request_body.workflow == mock_workflow.__dict__


def test_create_version_custom_name(
    version_manager: VersionManager,
    mock_workflows_client: WorkflowsApi,
    mock_workflow: Workflow,
):
    """Test version creation with custom name."""
    mock_response = Mock()
    mock_response.workflow_version_record.id = "version-456"
    mock_workflows_client.post_workflow_version = Mock(return_value=mock_response)

    result = version_manager.create_version(
        "project-123", "workflow-123", mock_workflow, version_name="custom-version"
    )

    assert result == "version-456"

    # Verify custom version name was used
    call_args = mock_workflows_client.post_workflow_version.call_args
    request_body = call_args[0][2]
    assert request_body.workflow_version_record.name == "custom-version"


def test_create_version_no_id_returned(
    version_manager: VersionManager,
    mock_workflows_client: WorkflowsApi,
    mock_workflow: Workflow,
):
    """Test error when no version ID is returned."""
    mock_response = Mock()
    mock_response.workflow_version_record.id = None
    mock_workflows_client.post_workflow_version = Mock(return_value=mock_response)

    with pytest.raises(Exception, match="Error creating workflow version"):
        version_manager.create_version("project-123", "workflow-123", mock_workflow)


@pytest.mark.parametrize(
    "version_id,expected_api_method,expected_api_args",
    [
        (None, "get_latest_workflow_version", ("project-123", "workflow-123")),
        (
            "version-456",
            "get_workflow_version",
            ("project-123", "workflow-123", "version-456"),
        ),
    ],
    ids=["latest_version", "specific_version"],
)
def test_read_version_success(
    version_manager: VersionManager,
    mock_workflow: Workflow,
    mock_workflows_client: WorkflowsApi,
    monkeypatch: MonkeyPatch,
    version_id: str | None,
    expected_api_method: str,
    expected_api_args: tuple[str, ...],
):
    """Test reading workflow versions (latest and specific)."""
    mock_response = Mock()
    mock_response.workflow = mock_workflow.__dict__

    api_method = getattr(mock_workflows_client, expected_api_method)
    api_method.return_value = mock_response

    mock_workflow_instance = Mock()
    MockWorkflow = Mock(return_value=mock_workflow_instance)
    monkeypatch.setattr(
        "uncertainty_engine.api_providers.workflows_provider.Workflow",
        MockWorkflow,
    )
    result = version_manager.read_version("project-123", "workflow-123", version_id)

    assert result == mock_workflow_instance
    api_method.assert_called_once_with(*expected_api_args)
    MockWorkflow.assert_called_once_with(
        graph={"nodes": [], "edges": []},
        input={"input1": "value1"},
        requested_output="output1",
        external_input_id="external-123",
    )


def test_read_version_no_data(
    version_manager: VersionManager, mock_workflows_client: WorkflowsApi
):
    """Test error when no workflow data is returned."""
    mock_response = Mock()
    mock_response.workflow = None
    mock_workflows_client.get_workflow_version = Mock(return_value=mock_response)

    with pytest.raises(
        Exception,
        match="Error reading workflow version: No workflow data found in the response.",
    ):
        version_manager.read_version("project-123", "workflow-123", "version-456")


def test_read_version_invalid_data(
    version_manager: VersionManager,
    mock_workflows_client: WorkflowsApi,
    monkeypatch: MonkeyPatch,
):
    """Test handling of invalid workflow data."""
    mock_response = Mock()
    mock_response.workflow = {"invalid": "data"}
    mock_workflows_client.get_workflow_version = Mock(return_value=mock_response)

    InvalidWorkflow = Mock()
    InvalidWorkflow.__dict__ = {"nodes": [], "edges": []}

    monkeypatch.setattr(
        "uncertainty_engine.api_providers.workflows_provider.Workflow", InvalidWorkflow
    )

    with pytest.raises(
        KeyError,
        match="Invalid Workflow object. Keys don't match: 'graph'",
    ):
        version_manager.read_version("project-123", "workflow-123", "version-456")


def test_read_version_api_exception(
    version_manager: VersionManager, mock_workflows_client: WorkflowsApi
):
    """Test handling of API exceptions during version reading."""
    mock_workflows_client.get_workflow_version = Mock(
        side_effect=ApiException(status=404, reason="Not Found")
    )

    with pytest.raises(Exception, match="Error reading workflow version"):
        version_manager.read_version("project-123", "workflow-123", "version-456")


def test_list_versions_success(
    version_manager: VersionManager, mock_workflows_client: WorkflowsApi
):
    """Test successful version listing."""
    mock_version = Mock(spec=WorkflowVersionRecordOutput)
    mock_response = Mock()
    mock_response.workflow_version_records = [mock_version]
    mock_workflows_client.get_workflow_version_records = Mock(
        return_value=mock_response
    )

    result = version_manager.list_versions("project-123", "workflow-123")

    assert result == [mock_version]
    mock_workflows_client.get_workflow_version_records.assert_called_once_with(
        "project-123", "workflow-123"
    )


def test_list_versions_api_exception(
    version_manager: VersionManager, mock_workflows_client: WorkflowsApi
):
    """Test handling of API exceptions during version listing."""
    mock_workflows_client.get_workflow_version_records = Mock(
        side_effect=ApiException(status=404, reason="Not Found")
    )

    with pytest.raises(Exception, match="Error reading workflow versions"):
        version_manager.list_versions("project-123", "workflow-123")
        version_manager.list_versions("project-123", "workflow-123")
        version_manager.list_versions("project-123", "workflow-123")
