import time
from unittest.mock import MagicMock, patch

import pytest

from uncertainty_engine.cognito_authenticator import CognitoToken

MOCK_ACCESS_TOKEN = "mock_access_token"
MOCK_REFRESH_TOKEN = "mock_refresh_token"


def test_init():
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    assert token.access_token == MOCK_ACCESS_TOKEN
    assert token.refresh_token == MOCK_REFRESH_TOKEN
    assert token._decoded_payload is None


def test_decoded_payload():
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "123", "username": "test_user"}
        decoded_payload = token.decoded_payload
        assert decoded_payload == {"sub": "123", "username": "test_user"}
        mock_decode.assert_called_once_with(
            MOCK_ACCESS_TOKEN, options={"verify_signature": False}
        )


def test_user_sub_id(monkeypatch):
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"sub": "value"})
    assert token.user_sub_id == "value"


def test_user_sub_id_exception(monkeypatch):
    with pytest.raises(KeyError):
        token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_sub": "value"})
        token.user_sub_id


def test_user_username_id(monkeypatch):
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"username": "value"})
    assert token.username == "value"


def test_user_username_id_exception(monkeypatch):
    with pytest.raises(KeyError):
        token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_username": "value"})
        token.username


def test_is_not_expired(monkeypatch):
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) + 3600,
        },
    )
    assert token.is_expired is False


def test_is_expired(monkeypatch):
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) - 3600,
        },
    )
    assert token.is_expired is True


def test_is_expired_invalid_token(monkeypatch):
    token = CognitoToken(MOCK_ACCESS_TOKEN, MOCK_REFRESH_TOKEN)
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {"not_exp": 1},
    )
    with pytest.raises(Exception) as excinfo:
        token.is_expired
    assert "Invalid token: Token did not include an expiry time" in str(excinfo.value)
