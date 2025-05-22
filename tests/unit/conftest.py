import json
import time
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

import boto3
import pytest

from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.cognito_authenticator import CognitoAuthenticator, CognitoToken


# Token values as fixtures
@pytest.fixture
def mock_access_token():
    return "mock_access_token"


@pytest.fixture
def mock_refresh_token():
    return "mock_refresh_token"


@pytest.fixture
def mock_id_token():
    return "mock_id_token"


@pytest.fixture
def mock_account_id():
    return "mock_account_id"


@pytest.fixture
def mock_deployment():
    return "mock_deployment"


# Common mock token data
@pytest.fixture
def mock_decoded_token():
    return {
        "sub": "mock_sub_id",
        "username": "mock_username",
        "exp": int(time.time()) + 18000,
    }


@pytest.fixture
def valid_token():
    current_timestamp = int(time.time())
    return {
        "exp": current_timestamp + 3600,
        "sub": "user123",
        "iss": "auth-service",
    }


# Auth fixtures
@pytest.fixture
def mock_cognito_token(
    mock_access_token: str,
    mock_refresh_token: str,
    mock_decoded_token: dict[str, str | int],
):
    mock_token = MagicMock(spec=CognitoToken)
    mock_token.access_token = mock_access_token
    mock_token.refresh_token = mock_refresh_token
    mock_token._decoded_payload = mock_decoded_token
    return mock_token


@pytest.fixture
def mock_cognito_authenticator(
    mock_access_token: str, mock_refresh_token: str, mock_id_token: str
):
    mock_authenticator = MagicMock(spec=CognitoAuthenticator)
    mock_authenticator.authenticate.return_value = {
        "access_token": mock_access_token,
        "refresh_token": mock_refresh_token,
    }
    mock_authenticator.get_access_token.return_value = mock_access_token
    mock_authenticator.refresh_tokens.return_value = {
        "access_token": mock_access_token,
        "id_token": mock_id_token,
        "expires_in": int(time.time() + 18000),
    }
    return mock_authenticator


@pytest.fixture
def mock_auth_service(mock_access_token: str, mock_account_id: str):
    auth_service = MagicMock(spec=AuthService)
    auth_service.refresh = MagicMock()
    auth_service.get_auth_header = MagicMock(
        return_value={"Authorization": f"Bearer {mock_access_token}"}
    )
    auth_service.account_id = mock_account_id
    return auth_service


@pytest.fixture
def mock_auth_file_data(
    mock_account_id: str, mock_access_token: str, mock_refresh_token: str
):
    """Default mock data for auth file"""
    return {
        "account_id": mock_account_id,
        "access_token": mock_access_token,
        "refresh_token": mock_refresh_token,
    }


# File operation fixtures
@pytest.fixture
def mock_file_content():
    """Default mock file content."""
    return b"test file content"


@pytest.fixture
def mock_file(mock_file_content: bytes):
    """Mock the open function for file operations."""
    _mock_file = mock_open(read_data=mock_file_content)
    with patch("builtins.open", _mock_file):
        yield _mock_file


# Cognito client fixtures
@pytest.fixture
def cognito_client():
    """Fixture to create a Cognito client with Stubber."""
    client = boto3.client("cognito-idp", region_name="eu-west-2")
    return client


# Auth service instances
@pytest.fixture
def auth_service_with_file(
    mock_cognito_authenticator: CognitoAuthenticator,
    mock_auth_file_data: dict[str, str],
):
    """Creates an AuthService instance with a mocked file that exists."""
    # Mock path for auth file
    mock_path = MagicMock()
    mock_path.exists.return_value = True  # File exists

    # Create a mock file handler using mock_open
    m = mock_open(read_data=json.dumps(mock_auth_file_data))

    # Create patches
    path_patch = patch.object(
        AuthService, "auth_file_path", new_callable=PropertyMock, return_value=mock_path
    )
    open_patch = patch("builtins.open", m)
    chmod_patch = patch("os.chmod")  # Mock os.chmod

    # Apply patches
    with path_patch, open_patch, chmod_patch:
        # Create AuthService instance
        auth_service = AuthService(mock_cognito_authenticator)
        yield auth_service, m  # Return both the service and the mock file handler


@pytest.fixture
def auth_service_no_file(mock_cognito_authenticator: CognitoAuthenticator):
    """Creates an AuthService instance with a mocked file that doesn't exist."""
    mock_path = MagicMock()
    mock_path.exists.return_value = False  # File doesn't exist

    path_patch = patch.object(
        AuthService, "auth_file_path", new_callable=PropertyMock, return_value=mock_path
    )

    with path_patch:
        auth_service = AuthService(mock_cognito_authenticator)
        yield auth_service
