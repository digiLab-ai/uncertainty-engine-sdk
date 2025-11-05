from unittest.mock import MagicMock

import pytest
from uncertainty_engine_resource_client.exceptions import UnauthorizedException

from tests.unit.api_providers.conftest import MockResource, MockResourceCustomFields
from uncertainty_engine.api_providers.api_provider import ApiProviderBase
from uncertainty_engine.auth_service import AuthService


class ApiProviderTestClass(ApiProviderBase):
    """
    A test API Provider class with a `make_api_call` function that can be made
    to fail after `n` calls.
    """

    def __init__(self, deployment: str, auth_service: AuthService):
        super().__init__(deployment, auth_service)
        self.auth_header = "Initial Auth Header"
        self.call_count = 0
        # Track number of consecutive failures to simulate
        self.fail_count = 0

    def set_fail_count(self, count: int):
        """Set how many consecutive calls should fail with UnauthorizedException"""
        self.fail_count = count
        self.call_count = 0

    def update_api_authentication(self) -> None:
        """Update auth header with token from auth_service"""
        self.auth_header = self.auth_service.get_auth_header()

    @ApiProviderBase.with_auth_refresh
    def make_api_call(self) -> str:
        """Test API method that will fail based on fail_count"""
        self.call_count += 1

        # If we still have failures to simulate
        if self.call_count <= self.fail_count:
            raise UnauthorizedException("Unauthorized")

        return f"Success with header: {self.auth_header}"

    @ApiProviderBase.with_auth_refresh
    def make_other_error_call(self):
        """Test API method that raises a different exception"""
        raise ValueError("Some other error")


# Tests for ApiProviderBase and with_auth_refresh decorator
def test_api_call_success(mock_auth_service: AuthService):
    """Test successful API call with no auth errors"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)
    provider.set_fail_count(0)  # No failures

    result = provider.make_api_call()

    assert "Success with header: Initial Auth Header" == result
    assert provider.call_count == 1
    mock_auth_service.refresh.assert_not_called()


def test_api_call_with_refresh(mock_auth_service: AuthService, mock_access_token: str):
    """Test API call that fails once but succeeds after token refresh"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)
    provider.set_fail_count(1)  # Fail first call

    result = provider.make_api_call()

    assert provider.call_count == 2
    mock_auth_service.refresh.assert_called_once()
    mock_auth_service.get_auth_header.assert_called_once()
    assert (
        result
        == f"Success with header: {{'Authorization': 'Bearer {mock_access_token}'}}"
    )


def test_api_call_other_exception(mock_auth_service: AuthService):
    """Test API call that raises a non-auth exception"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    with pytest.raises(ValueError, match="Some other error"):
        provider.make_other_error_call()

    mock_auth_service.refresh.assert_not_called()


def test_update_api_authentication_not_implemented():
    """Test that the base class's update_api_authentication raises NotImplementedError"""
    base_provider = ApiProviderBase("test-deployment", MagicMock())

    with pytest.raises(NotImplementedError):
        base_provider.update_api_authentication()


def test_strips_endpoint(mock_auth_service: AuthService) -> None:
    base_provider = ApiProviderBase("test-deployment/", mock_auth_service)
    assert base_provider.deployment == "test-deployment"


def test_get_id_by_name_success(
    mock_auth_service: AuthService,
    mock_resources: list[MockResource],
):
    """Test successful ID retrieval with default field names"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    def list_func() -> list[MockResource]:
        return mock_resources

    result = provider.get_id_by_name(list_func, "resource_two", "resource")

    assert result == "2"


def test_get_id_by_name_with_custom_fields(
    mock_auth_service: AuthService,
    mock_resources_custom_fields: list[MockResourceCustomFields],
):
    """Test successful ID retrieval with custom field names"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    def list_func():
        return mock_resources_custom_fields

    result = provider.get_id_by_name(
        list_func,
        "custom_two",
        "custom_resource",
        name_field="other_name",
        id_field="_id",
    )

    assert result == "102"


def test_get_id_by_name_not_found(
    mock_auth_service: AuthService,
    mock_resources: list[MockResource],
):
    """Test ValueError when resource name is not found"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    def list_func():
        return mock_resources

    with pytest.raises(ValueError, match="No resource found with name: nonexistent"):
        provider.get_id_by_name(list_func, "nonexistent", "resource")


def test_get_id_by_name_empty_list(mock_auth_service: AuthService):
    """Test ValueError when list is empty"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    def list_func() -> list[MockResource]:
        return []

    with pytest.raises(ValueError, match="No resource found with name: any_name"):
        provider.get_id_by_name(list_func, "any_name", "resource")


def test_get_id_by_name_no_resource_type(
    mock_auth_service: AuthService,
    mock_resources: list[MockResource],
):
    """Test error message when resource_type is empty"""
    provider = ApiProviderTestClass("test-deployment", mock_auth_service)

    def list_func():
        return mock_resources

    with pytest.raises(ValueError, match="No item found with name: nonexistent"):
        provider.get_id_by_name(list_func, "nonexistent")
