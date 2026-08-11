import json
import os
from pathlib import Path
from unittest.mock import MagicMock, PropertyMock, mock_open, patch

import pytest
from pytest import MonkeyPatch, mark

from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.cognito_authenticator import CognitoAuthenticator, CognitoToken
from uncertainty_engine.types import GetResourceToken


@pytest.fixture
def auth_service_with_real_file(
    tmp_path: Path,
    mock_cognito_authenticator: CognitoAuthenticator,
    mock_get_resource_token: GetResourceToken,
    mock_auth_file_data: dict[str, str],
):
    """Creates an AuthService instance backed by a real auth file on disk."""
    auth_file = tmp_path / ".ue_auth"
    auth_file.write_text(json.dumps(mock_auth_file_data))

    with patch.object(
        AuthService,
        "auth_file_path",
        new_callable=PropertyMock,
        return_value=auth_file,
    ):
        auth_service = AuthService(
            mock_cognito_authenticator,
            mock_get_resource_token,
        )

        yield auth_service, auth_file


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
    monkeypatch: MonkeyPatch,
):
    """Test successful authentication"""
    # Setup
    username = "test_user"
    password = "test_password"
    account_id = "test_account"

    # Set environment variables using monkeypatch
    monkeypatch.setenv("UE_USERNAME", username)
    monkeypatch.setenv("UE_PASSWORD", password)

    # Call authenticate
    auth_service_no_file.authenticate()

    # Verify authenticator was called with correct params
    mock_cognito_authenticator.authenticate.assert_called_once_with(username, password)

    # Verify token and account_id were set
    assert auth_service_no_file.account_id == account_id
    assert auth_service_no_file.token is not None
    assert auth_service_no_file.is_authenticated is True


@mark.parametrize(
    "preset_id, expected_id",
    [
        ("preset_account_id", "preset_account_id"),
        (None, "test_account"),
    ],
)
def test_authenticate_only_updates_account_id_when_none(
    preset_id: str | None,
    expected_id: str,
    auth_service_no_file: AuthService,
    monkeypatch: MonkeyPatch,
):
    """Test authentication only updates the `account_id` when `None`."""
    username = "test_user"
    password = "test_password"

    monkeypatch.setenv("UE_USERNAME", username)
    monkeypatch.setenv("UE_PASSWORD", password)

    auth_service_no_file.account_id = preset_id
    auth_service_no_file.authenticate()

    assert auth_service_no_file.account_id == expected_id


def test_authenticate_from_env_vars(
    auth_service_no_file: AuthService,
    mock_cognito_authenticator: CognitoAuthenticator,
    monkeypatch: MonkeyPatch,
):
    """Test authentication using environment variables"""
    # Setup
    env_username = "env_user"
    env_password = "env_password"

    # Set environment variables using monkeypatch
    monkeypatch.setenv("UE_USERNAME", env_username)
    monkeypatch.setenv("UE_PASSWORD", env_password)

    # Call authenticate without username/password
    auth_service_no_file.authenticate()

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
        auth_service_no_file.authenticate()

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


def test_auth_file_path(mock_get_resource_token: GetResourceToken) -> None:
    """Test auth_file_path property"""
    # Create service with mock authenticator
    authenticator = MagicMock()
    service = AuthService(
        authenticator,
        mock_get_resource_token,
    )

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
    auth_service.auth_file_path.unlink.assert_called_once_with(
        missing_ok=True,
    )


def test_refresh_successful(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_cognito_authenticator: CognitoAuthenticator,
    mock_refreshed_cognito_tokens: CognitoToken,
    monkeypatch,
):
    """Test successful token refresh"""
    auth_service, _ = auth_service_with_file

    # Mock _save_to_file
    monkeypatch.setattr(auth_service, "_save_to_file", lambda: None)

    # Refresh token
    result = auth_service.refresh()

    # Verify token was refreshed
    assert result is auth_service.token
    assert auth_service.token == mock_refreshed_cognito_tokens

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
    auth_service_with_real_file: tuple[AuthService, Path],
    mock_cognito_authenticator: CognitoAuthenticator,
    mock_auth_file_data: dict[str, str],
):
    """
    A failed refresh clears the in-memory token but leaves the shared
    cache file alone: a concurrent process may have just saved fresh,
    valid tokens to it.
    """
    auth_service, auth_file = auth_service_with_real_file

    # Setup authenticator to raise exception
    error_message = "Token expired"
    mock_cognito_authenticator.refresh_tokens.side_effect = Exception(error_message)

    # Verify refresh raises error
    with pytest.raises(ValueError) as excinfo:
        auth_service.refresh()

    assert f"Failed to refresh token: {error_message}" in str(excinfo.value)

    # The in-memory token is cleared...
    assert auth_service.token is None

    # ...but the shared cache file is untouched.
    assert json.loads(auth_file.read_text()) == mock_auth_file_data


def test_refresh_save_failure_keeps_token(
    auth_service_with_real_file: tuple[AuthService, Path],
    mock_refreshed_cognito_tokens: CognitoToken,
    mock_auth_file_data: dict[str, str],
):
    """
    If the refresh succeeds but saving to the cache fails, the new
    token is kept and returned with a warning, and the cache file is
    neither replaced nor deleted.
    """
    auth_service, auth_file = auth_service_with_real_file

    with patch.object(
        auth_service,
        "_save_to_file",
        side_effect=OSError("disk full"),
    ):
        with pytest.warns(UserWarning, match="disk full"):
            result = auth_service.refresh()

    # The refreshed token is kept in memory and returned.
    assert result is auth_service.token
    assert auth_service.token == mock_refreshed_cognito_tokens

    # The cache file still holds the previous tokens.
    assert json.loads(auth_file.read_text()) == mock_auth_file_data


def test_get_auth_header(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_access_token: str,
    mock_resource_token: str,
):
    """Test getting authorization header"""
    auth_service, _ = auth_service_with_file

    # Get auth header
    headers = auth_service.get_auth_header()

    # Verify header format
    assert headers == {
        "Authorization": f"Bearer {mock_access_token}",
        "X-Resource-Service-Token": mock_resource_token,
    }


def test_get_auth_header_with_id(
    auth_service_with_file: tuple[AuthService, MagicMock],
    mock_access_token: str,
    mock_id_token: str,
    mock_resource_token: str,
) -> None:
    auth_service, _ = auth_service_with_file

    headers = auth_service.get_auth_header(include_id=True)

    assert headers == {
        "Authorization": f"Bearer {mock_access_token}",
        "X-ID-Token": mock_id_token,
        "X-Resource-Service-Token": mock_resource_token,
    }


def test_get_auth_header_not_authenticated(auth_service_no_file: AuthService):
    """Test get_auth_header fails when not authenticated"""
    with pytest.raises(ValueError) as excinfo:
        auth_service_no_file.get_auth_header()

    assert "Not authenticated" in str(excinfo.value)


def test_save_to_file(auth_service_with_real_file: tuple[AuthService, Path]):
    """Test saving to file"""
    auth_service, auth_file = auth_service_with_real_file

    # Set new values
    auth_service.token.access_token = "new_access_token"
    auth_service.account_id = "new_account_id"

    # Call _save_to_file
    auth_service._save_to_file()

    parsed_data = json.loads(auth_file.read_text())

    assert parsed_data["access_token"] == "new_access_token"
    assert parsed_data["account_id"] == "new_account_id"

    # The temporary file used for the atomic write must not be left behind
    assert [p.name for p in auth_file.parent.iterdir()] == [auth_file.name]


# os.name == "nt": skip on Windows.
@mark.skipif(os.name == "nt", reason="Checks POSIX file permissions")
def test_save_to_file_permissions(
    auth_service_with_real_file: tuple[AuthService, Path],
) -> None:
    """The saved auth file is only readable by its owner."""
    auth_service, auth_file = auth_service_with_real_file

    auth_service._save_to_file()

    assert auth_file.stat().st_mode & 0o777 == 0o600


def test_save_to_file_retries_replace_on_permission_error(
    auth_service_with_real_file: tuple[AuthService, Path],
) -> None:
    """
    A transient sharing violation (Windows) is retried rather than
    raised.
    """
    auth_service, _ = auth_service_with_real_file

    with patch(
        "os.replace",
        side_effect=[PermissionError("sharing violation"), None],
    ) as mock_replace:
        auth_service._save_to_file()

    assert mock_replace.call_count == 2


def test_save_to_file_replace_retries_exhausted(
    auth_service_with_real_file: tuple[AuthService, Path],
    mock_auth_file_data: dict[str, str],
) -> None:
    """
    A persistent sharing violation is raised, leaving no temporary
    files.
    """
    auth_service, auth_file = auth_service_with_real_file

    with patch(
        "os.replace",
        side_effect=PermissionError("sharing violation"),
    ):
        with patch("time.sleep") as mock_sleep:
            with pytest.raises(PermissionError):
                auth_service._save_to_file()

    assert mock_sleep.call_count == 4
    assert json.loads(auth_file.read_text()) == mock_auth_file_data
    assert [p.name for p in auth_file.parent.iterdir()] == [
        auth_file.name,
    ]


def test_save_to_file_cleans_up_temp_file_on_failure(
    auth_service_with_real_file: tuple[AuthService, Path],
    mock_auth_file_data: dict[str, str],
) -> None:
    """
    A failed save leaves the previous auth file intact and no temporary
    files.
    """
    auth_service, auth_file = auth_service_with_real_file

    with patch("json.dump", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            auth_service._save_to_file()

    assert json.loads(auth_file.read_text()) == mock_auth_file_data
    assert [p.name for p in auth_file.parent.iterdir()] == [auth_file.name]


def test_load_from_file_exception(auth_service_no_file: AuthService):
    """Test error handling when loading from file"""
    # Mock file exists but has invalid content
    with patch.object(auth_service_no_file.auth_file_path, "exists", return_value=True):
        with patch("builtins.open", side_effect=Exception("Invalid JSON")):
            # Verify load raises exception
            with pytest.raises(Exception) as excinfo:
                auth_service_no_file._load_from_file()

            assert "Error loading authentication details" in str(excinfo.value)


def test_load_from_file_deleted_mid_read(
    auth_service_no_file: AuthService,
) -> None:
    """
    A file deleted between the existence check and the read is treated
    as missing.
    """
    with patch.object(
        auth_service_no_file.auth_file_path,
        "exists",
        return_value=True,
    ):
        with patch("builtins.open", side_effect=FileNotFoundError()):
            auth_service_no_file._load_from_file()

    assert auth_service_no_file.token is None


@mark.parametrize(
    "content",
    [
        "",  # e.g. read mid-write by a non-atomic writer
        '{"account_id": "test_ac',  # e.g. an interrupted write
        "null",  # valid JSON, but not an object
    ],
)
def test_load_from_file_unreadable(
    auth_service_no_file: AuthService,
    content: str,
) -> None:
    """
    An empty, corrupt or non-object cache file is ignored with a warning.
    """
    with patch.object(
        auth_service_no_file.auth_file_path,
        "exists",
        return_value=True,
    ):
        with patch("builtins.open", mock_open(read_data=content)):
            with pytest.warns(UserWarning, match="authentication cache"):
                auth_service_no_file._load_from_file()

    assert auth_service_no_file.token is None


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
