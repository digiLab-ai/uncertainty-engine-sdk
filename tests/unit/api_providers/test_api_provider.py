import time
from unittest.mock import MagicMock

import pytest
from uncertainty_engine_resource_client.exceptions import UnauthorizedException

from uncertainty_engine.api_providers.api_provider import MAX_RETRIES, ApiProviderBase
from uncertainty_engine.auth_service import AuthService


@pytest.fixture
def valid_token():
    current_timestamp = int(time.time())
    return {
        "exp": current_timestamp + 3600,  # Expires 1 hour in the future
        "sub": "user123",
        "iss": "auth-service",
    }


@pytest.fixture
def mock_auth_service():
    auth_service = MagicMock(spec=AuthService)
    auth_service.refresh = MagicMock()
    auth_service.get_auth_header = MagicMock(
        return_value={"Authorization": "Bearer fresh_token"}
    )
    return auth_service


class TestApiProvider(ApiProviderBase):
    """
    A test API Provider class with a `make_api_call` function that can be made
    to fail after `n` calls.
    """

    def __init__(self, deployment, auth_service):
        super().__init__(deployment, auth_service)
        self.auth_header = "Initial Auth Header"
        self.call_count = 0
        # Track number of consecutive failures to simulate
        self.fail_count = 0

    def set_fail_count(self, count):
        """Set how many consecutive calls should fail with UnauthorizedException"""
        self.fail_count = count
        self.call_count = 0

    def update_api_authentication(self):
        """Update auth header with token from auth_service"""
        self.auth_header = self.auth_service.get_auth_header()

    @ApiProviderBase.with_auth_refresh
    def make_api_call(self):
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
def test_api_call_success(mock_auth_service):
    """Test successful API call with no auth errors"""
    provider = TestApiProvider("test-deployment", mock_auth_service)
    provider.set_fail_count(0)  # No failures

    result = provider.make_api_call()

    assert "Success with header: Initial Auth Header" == result
    assert provider.call_count == 1
    mock_auth_service.refresh.assert_not_called()


def test_api_call_with_single_refresh(mock_auth_service):
    """Test API call that fails once but succeeds after token refresh"""
    provider = TestApiProvider("test-deployment", mock_auth_service)
    provider.set_fail_count(1)  # Fail first call

    result = provider.make_api_call()

    assert provider.call_count == 2  # Initial call + retry
    mock_auth_service.refresh.assert_called_once()
    mock_auth_service.get_auth_header.assert_called_once()
    assert "Success with header: {'Authorization': 'Bearer fresh_token'}" == result


def test_api_call_with_max_retries(mock_auth_service):
    """Test API call that uses exactly MAX_RETRIES and succeeds"""
    provider = TestApiProvider("test-deployment", mock_auth_service)

    # Fail exactly MAX_RETRIES times
    provider.set_fail_count(MAX_RETRIES)
    result = provider.make_api_call()

    # Initial call + MAX_RETRIES
    assert provider.call_count == MAX_RETRIES + 1
    assert mock_auth_service.refresh.call_count == MAX_RETRIES
    assert "Success with header: {'Authorization': 'Bearer fresh_token'}" == result


def test_api_call_exceeds_max_retries(mock_auth_service):
    """Test API call that still fails after MAX_RETRIES refreshes"""
    provider = TestApiProvider("test-deployment", mock_auth_service)

    # Fail more than MAX_RETRIES times
    provider.set_fail_count(MAX_RETRIES + 1)

    # Should raise UnauthorizedException after exhausting retries
    with pytest.raises(UnauthorizedException):
        provider.make_api_call()

    # Should have attempted exactly MAX_RETRIES + 1 calls (initial + MAX_RETRIES)
    assert provider.call_count == MAX_RETRIES + 1
    assert mock_auth_service.refresh.call_count == MAX_RETRIES


def test_api_call_other_exception(mock_auth_service):
    """Test API call that raises a non-auth exception"""
    provider = TestApiProvider("test-deployment", mock_auth_service)

    with pytest.raises(ValueError, match="Some other error"):
        provider.make_other_error_call()

    mock_auth_service.refresh.assert_not_called()


def test_update_api_authentication_not_implemented():
    """Test that the base class's update_api_authentication raises NotImplementedError"""
    base_provider = ApiProviderBase("test-deployment", MagicMock())

    with pytest.raises(NotImplementedError):
        base_provider.update_api_authentication()
