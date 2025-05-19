import time
from unittest.mock import patch

import pytest

from uncertainty_engine.cognito_authenticator import CognitoToken


def test_init(mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    assert token.access_token == mock_access_token
    assert token.refresh_token == mock_refresh_token
    assert token._decoded_payload is None


def test_decoded_payload(mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "123", "username": "test_user"}
        decoded_payload = token.decoded_payload
        assert decoded_payload == {"sub": "123", "username": "test_user"}
        mock_decode.assert_called_once_with(
            mock_access_token, options={"verify_signature": False}
        )


def test_user_sub_id(monkeypatch, mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"sub": "value"})
    assert token.user_sub_id == "value"


def test_user_sub_id_exception(monkeypatch, mock_access_token, mock_refresh_token):
    with pytest.raises(KeyError):
        token = CognitoToken(mock_access_token, mock_refresh_token)
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_sub": "value"})
        token.user_sub_id


def test_user_username_id(monkeypatch, mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"username": "value"})
    assert token.username == "value"


def test_user_username_id_exception(monkeypatch, mock_access_token, mock_refresh_token):
    with pytest.raises(KeyError):
        token = CognitoToken(mock_access_token, mock_refresh_token)
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_username": "value"})
        token.username


def test_is_not_expired(monkeypatch, mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) + 3600,
        },
    )
    assert token.is_expired is False


def test_is_expired(monkeypatch, mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) - 3600,
        },
    )
    assert token.is_expired is True


def test_is_expired_invalid_token(monkeypatch, mock_access_token, mock_refresh_token):
    token = CognitoToken(mock_access_token, mock_refresh_token)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {"not_exp": 1},
    )
    with pytest.raises(Exception) as excinfo:
        token.is_expired
    assert "Invalid token: Token did not include an expiry time" in str(excinfo.value)
