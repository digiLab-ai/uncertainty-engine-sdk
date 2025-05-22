import json
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.cognito_authenticator import CognitoAuthenticator


def test_init_no_file(auth_service_no_file: AuthService):
    """Test that a new AuthService has no account_id set."""
    assert auth_service_no_file.account_id is None
    assert auth_service_no_file.token is None
    assert auth_service_no_file.is_authenticated is False


def test_init_with_file(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_access_token: str,
    mock_account_id: str,
):
    """Test initialization with auth file"""
    auth_service, _ = auth_service_with_file

    assert auth_service.account_id == mock_account_id
    assert auth_service.token is not None
    assert auth_service.token.access_token == mock_access_token
    assert auth_service.is_authenticated is True


def test_authenticate(
    auth_service_no_file: AuthService,
    mock_cognito_authenticator: CognitoAuthenticator,
    monkeypatch,
):
    """Test successful authentication"""
    # Setup
    username = "test_user"
    password = "test_password"
    account_id = "test_account"

    # Mock save_to_file to prevent actual file operations
    monkeypatch.setattr(auth_service_no_file, "_save_to_file", lambda: None)

    # Set environment variables using monkeypatch
    monkeypatch.setenv("UE_USERNAME", username)
    monkeypatch.setenv("UE_PASSWORD", password)

    # Call authenticate
    auth_service_no_file.authenticate(account_id)

    # Verify authenticator was called with correct params
    mock_cognito_authenticator.authenticate.assert_called_once_with(username, password)

    # Verify token and account_id were set
    assert auth_service_no_file.account_id == account_id
    assert auth_service_no_file.token is not None
    assert auth_service_no_file.is_authenticated is True


def test_authenticate_from_env_vars(
    auth_service_no_file: AuthService,
    mock_cognito_authenticator: CognitoAuthenticator,
    monkeypatch,
):
    """Test authentication using environment variables"""
    # Setup
    account_id = "test_account"
    env_username = "env_user"
    env_password = "env_password"

    # Set environment variables using monkeypatch
    monkeypatch.setenv("UE_USERNAME", env_username)
    monkeypatch.setenv("UE_PASSWORD", env_password)

    # Mock save_to_file to prevent actual file operations
    monkeypatch.setattr(auth_service_no_file, "_save_to_file", lambda: None)

    # Call authenticate without username/password
    auth_service_no_file.authenticate(account_id)

    # Verify authenticator was called with env vars
    mock_cognito_authenticator.authenticate.assert_called_once_with(
        env_username, env_password
    )


def test_authenticate_missing_credentials(
    auth_service_no_file: AuthService, monkeypatch
):
    """Test authentication fails when no credentials provided"""
    # Clear environment variables using monkeypatch
    monkeypatch.delenv("UE_USERNAME", raising=False)
    monkeypatch.delenv("UE_PASSWORD", raising=False)

    # Verify authentication raises error
    with pytest.raises(ValueError) as excinfo:
        auth_service_no_file.authenticate("test_account")

    assert "Username and password must be provided" in str(excinfo.value)


def test_is_authenticated_property(auth_service_no_file: AuthService):
    """Test is_authenticated property"""
    # Initially not authenticated
    assert auth_service_no_file.is_authenticated is False

    # Set token but not account_id
    auth_service_no_file.token = MagicMock()
    assert auth_service_no_file.is_authenticated is False

    # Set account_id but not token
    auth_service_no_file.token = None
    auth_service_no_file.account_id = "test_account"
    assert auth_service_no_file.is_authenticated is False

    # Set both token and account_id
    auth_service_no_file.token = MagicMock()
    auth_service_no_file.account_id = "test_account"
    assert auth_service_no_file.is_authenticated is True


def test_auth_file_path():
    """Test auth_file_path property"""
    # Create service with mock authenticator
    authenticator = MagicMock()
    service = AuthService(authenticator)

    # Verify auth_file_path
    expected_path = Path.home() / ".ue_auth"
    assert service.auth_file_path == expected_path


def test_clear(auth_service_with_file: tuple[AuthService, MagicMock]):
    """Test clearing auth data"""
    auth_service, _ = auth_service_with_file

    # Mock unlink method to track calls
    auth_service.auth_file_path.unlink = MagicMock()

    # Call clear
    auth_service.clear()

    # Verify token is cleared
    assert auth_service.token is None

    # Verify unlink was called
    auth_service.auth_file_path.unlink.assert_called_once()


def test_refresh_successful(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_cognito_authenticator: CognitoAuthenticator,
    monkeypatch,
):
    """Test successful token refresh"""
    auth_service, _ = auth_service_with_file

    # Setup new token values
    new_access_token = "new_access_token"
    mock_cognito_authenticator.refresh_tokens.return_value = {
        "access_token": new_access_token
    }

    # Mock _save_to_file
    monkeypatch.setattr(auth_service, "_save_to_file", lambda: None)

    # Refresh token
    result = auth_service.refresh()

    # Verify token was refreshed
    assert result is auth_service.token
    assert auth_service.token.access_token == new_access_token

    # Verify authenticator was called with refresh token
    mock_cognito_authenticator.refresh_tokens.assert_called_once_with(
        auth_service.token.refresh_token
    )


def test_refresh_no_token(auth_service_no_file: AuthService):
    """Test refresh fails when no token available"""
    with pytest.raises(ValueError) as excinfo:
        auth_service_no_file.refresh()

    assert "No refresh token available" in str(excinfo.value)


def test_refresh_exception(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_cognito_authenticator: CognitoAuthenticator,
):
    """Test refresh error handling"""
    auth_service, _ = auth_service_with_file

    # Setup authenticator to raise exception
    error_message = "Token expired"
    mock_cognito_authenticator.refresh_tokens.side_effect = Exception(error_message)

    # Mock clear method
    with patch.object(auth_service, "clear"):
        # Verify refresh raises error
        with pytest.raises(ValueError) as excinfo:
            auth_service.refresh()

        assert f"Failed to refresh token: {error_message}" in str(excinfo.value)

        # Verify clear was called
        auth_service.clear.assert_called_once()


def test_get_auth_header(auth_service_with_file: tuple[AuthService, MagicMock]):
    """Test getting authorization header"""
    auth_service, _ = auth_service_with_file

    # Get auth header
    header = auth_service.get_auth_header()

    # Verify header format
    assert header == {"Authorization": f"Bearer {auth_service.token.access_token}"}


def test_get_auth_header_not_authenticated(auth_service_no_file: AuthService):
    """Test get_auth_header fails when not authenticated"""
    with pytest.raises(ValueError) as excinfo:
        auth_service_no_file.get_auth_header()

    assert "Not authenticated" in str(excinfo.value)


def test_save_to_file(auth_service_with_file: tuple[AuthService, MagicMock]):
    """Test saving to file"""
    auth_service, mock_file = auth_service_with_file

    # Set new values
    auth_service.token.access_token = "new_access_token"
    auth_service.account_id = "new_account_id"

    # Call _save_to_file
    auth_service._save_to_file()

    # Check what was written to the file
    # Get all write calls and join them
    written_data = "".join(call.args[0] for call in mock_file().write.call_args_list)
    parsed_data = json.loads(written_data)

    assert parsed_data["access_token"] == "new_access_token"
    assert parsed_data["account_id"] == "new_account_id"


def test_load_from_file_exception(auth_service_no_file: AuthService):
    """Test error handling when loading from file"""
    # Mock file exists but has invalid content
    with patch.object(auth_service_no_file.auth_file_path, "exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Invalid JSON")):
            # Verify load raises exception
            with pytest.raises(Exception) as excinfo:
                auth_service_no_file._load_from_file()

            assert "Error loading authentication details" in str(excinfo.value)


def test_load_from_file_missing_keys(auth_service_no_file: AuthService):
    """Test handling incomplete data in auth file"""
    # Mock file exists with incomplete data
    incomplete_data = json.dumps({"account_id": "test_account"})  # Missing tokens

    with patch.object(auth_service_no_file.auth_file_path, "exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=incomplete_data)):
            # Call _load_from_file - shouldn't set token/account_id due to missing keys
            auth_service_no_file._load_from_file()

            # Verify token and account_id weren't set
            assert auth_service_no_file.token is None
