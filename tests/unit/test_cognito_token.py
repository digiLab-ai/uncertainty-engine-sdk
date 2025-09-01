import time
from unittest.mock import patch

import pytest
from pytest import MonkeyPatch, fixture

from uncertainty_engine.cognito_authenticator import CognitoToken


@fixture
def token() -> CognitoToken:
    return CognitoToken(
        "access",
        "refresh",
        "id",
    )


def test_eq(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "refresh",
        "id",
    )

    assert token == b


def test_eq_different_type(token: CognitoToken) -> None:
    b = "not a token"

    assert token != b


def test_eq_different_access(token: CognitoToken) -> None:
    b = CognitoToken(
        "different_access",
        "refresh",
        "id",
    )

    assert token != b


def test_eq_different_refresh(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "different_refresh",
        "id",
    )

    assert token != b


def test_eq_different_id(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "refresh",
        "different_id",
    )

    assert token != b


def test_hash(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "refresh",
        "id",
    )

    assert hash(token) == hash(b)


def test_hash_different_access(token: CognitoToken) -> None:
    b = CognitoToken(
        "different_access",
        "refresh",
        "id",
    )

    assert hash(token) != hash(b)


def test_hash_different_refresh(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "different_refresh",
        "id",
    )

    assert hash(token) != hash(b)


def test_hash_different_id(token: CognitoToken) -> None:
    b = CognitoToken(
        "access",
        "refresh",
        "different_id",
    )

    assert hash(token) != hash(b)


def test_init(
    mock_access_token: str,
    mock_id_token: str,
    mock_refresh_token: str,
) -> None:
    token = CognitoToken(
        mock_access_token,
        mock_refresh_token,
        mock_id_token,
    )

    assert token.access_token == mock_access_token
    assert token.id_token == mock_id_token
    assert token.refresh_token == mock_refresh_token


def test_decoded_payload(token: CognitoToken) -> None:
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "123", "username": "test_user"}
        decoded_payload = token.decoded_payload
        assert decoded_payload == {"sub": "123", "username": "test_user"}
        mock_decode.assert_called_once_with(
            token.access_token,
            options={"verify_signature": False},
        )


def test_user_sub_id(
    monkeypatch: MonkeyPatch,
    token: CognitoToken,
) -> None:
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"sub": "value"})
    assert token.user_sub_id == "value"


def test_user_sub_id_exception(
    monkeypatch: MonkeyPatch,
    token: CognitoToken,
) -> None:
    with pytest.raises(KeyError):
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_sub": "value"})
        token.user_sub_id


def test_user_username_id(
    monkeypatch: MonkeyPatch,
    token: CognitoToken,
) -> None:
    monkeypatch.setattr(CognitoToken, "decoded_payload", {"username": "value"})
    assert token.username == "value"


def test_user_username_id_exception(
    monkeypatch: MonkeyPatch,
    token: CognitoToken,
) -> None:
    with pytest.raises(KeyError):
        monkeypatch.setattr(CognitoToken, "decoded_payload", {"not_username": "value"})
        token.username


def test_is_not_expired(monkeypatch: MonkeyPatch, token: CognitoToken) -> None:
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) + 3600,
        },
    )
    assert token.is_expired is False


def test_is_expired(monkeypatch: MonkeyPatch, token: CognitoToken) -> None:
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {
            "exp": int(time.time()) - 3600,
        },
    )
    assert token.is_expired is True


def test_is_expired_invalid_token(
    monkeypatch: MonkeyPatch,
    token: CognitoToken,
) -> None:
    monkeypatch.setattr(
        CognitoToken,
        "decoded_payload",
        {"not_exp": 1},
    )
    with pytest.raises(Exception) as excinfo:
        token.is_expired
    assert "Invalid token: Token did not include an expiry time" in str(excinfo.value)
