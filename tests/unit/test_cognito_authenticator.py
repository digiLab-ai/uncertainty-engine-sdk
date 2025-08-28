from unittest.mock import patch

import pytest
from botocore.stub import Stubber
from mypy_boto3_cognito_idp.client import CognitoIdentityProviderClient
from pytest import FixtureRequest

from uncertainty_engine.cognito_authenticator import CognitoAuthenticator, CognitoToken


@pytest.fixture
def cognito_client_stub(
    request: FixtureRequest, cognito_client: CognitoIdentityProviderClient
):

    # Get the stubber for the client
    stubber = Stubber(cognito_client)

    # Set up the stubber to expect the initiate_auth call
    stubber.add_response(
        request.param.get("method", ""),
        request.param.get("response", {}),
        request.param.get("method_args", {}),
    )

    # Activate the stub to block boto3 client calls and use the stubbed responses instead
    stubber.activate()

    with patch("boto3.client") as mock_client:
        mock_client.return_value = cognito_client
        yield mock_client
        stubber.assert_no_pending_responses()


@pytest.fixture()
def cognito_client_exception_stub(
    request: FixtureRequest, cognito_client: CognitoIdentityProviderClient
):

    # Get the stubber for the client
    stubber = Stubber(cognito_client)

    # Set up the stubber to expect the initiate_auth call
    stubber.add_client_error(
        request.param.get("method", ""),
        request.param.get("code", ""),
        request.param.get("message", ""),
    )

    # Activate the stub to block boto3 client calls and use the stubbed responses instead
    stubber.activate()

    with patch("boto3.client") as mock_client:
        mock_client.return_value = cognito_client
        yield mock_client
        # TODO: Is this just only required for succesful requests/responses?
        # stubber.assert_no_pending_responses()


@pytest.fixture
def authenticator_args():
    return {
        "region": "eu-west-2",
        "client_id": "1234567890abcdef",
    }


def test_init(
    cognito_client: CognitoIdentityProviderClient, authenticator_args: dict[str, str]
):
    """Test the initialization of CognitoAuthenticator."""

    # Patch boto3.client to return our fixture client when called with the correct parameters
    with patch("boto3.client") as mock_client:
        mock_client.return_value = cognito_client

        authenticator = CognitoAuthenticator(**authenticator_args)

        assert authenticator.region == authenticator_args["region"]
        assert authenticator.client_id == authenticator_args["client_id"]
        assert authenticator.client == cognito_client
        mock_client.assert_called_once_with(
            "cognito-idp", region_name=authenticator_args["region"]
        )


@pytest.mark.parametrize(
    "cognito_client_stub",
    [
        {
            "method": "initiate_auth",
            "response": {
                "AuthenticationResult": {
                    "AccessToken": "mock_access_token",
                    "IdToken": "mock_id_token",
                    "RefreshToken": "mock_refresh_token",
                    "ExpiresIn": 3600,
                    "TokenType": "Bearer",
                }
            },
            "method_args": {
                "AuthFlow": "USER_PASSWORD_AUTH",
                "ClientId": "1234567890abcdef",
                "AuthParameters": {"USERNAME": "testuser", "PASSWORD": "testpassword"},
            },
        }
    ],
    indirect=True,
)
def test_authenticate(
    cognito_client_stub,
    authenticator_args: dict[str, str],
    mock_access_token: str,
    mock_id_token: str,
    mock_refresh_token: str,
):
    """Test the authenticate method of CognitoAuthenticator."""

    username = "testuser"
    password = "testpassword"

    authenticator = CognitoAuthenticator(**authenticator_args)
    token = authenticator.authenticate(username, password)

    expected_token = CognitoToken(
        mock_access_token,
        mock_refresh_token,
        mock_id_token,
    )

    assert token == expected_token


@pytest.mark.parametrize(
    "cognito_client_exception_stub, error",
    [
        (
            {"method": "initiate_auth", "code": "NotAuthorizedException"},
            "Invalid username or password.",
        ),
        (
            {"method": "initiate_auth", "code": "UserNotFoundException"},
            "User not found.",
        ),
        (
            {"method": "initiate_auth", "code": "PasswordResetRequiredException"},
            "Password reset required.",
        ),
        (
            {"method": "initiate_auth", "code": "UserNotConfirmedException"},
            "User account is not verified.",
        ),
        (
            {
                "method": "initiate_auth",
                "code": "ClientError",
                "message": "Unknown Error",
            },
            "Authentication failed: Unknown Error",
        ),
    ],
    indirect=["cognito_client_exception_stub"],
)
def test_authenticate_client_exceptions(
    cognito_client_exception_stub, error: str, authenticator_args: dict[str, str]
):
    """Test the authenticate method of CognitoAuthenticator."""

    with pytest.raises(Exception) as excinfo:
        authenticator = CognitoAuthenticator(**authenticator_args)
        authenticator.authenticate("testuser", "testpassword")
    assert error == str(excinfo.value)


@pytest.mark.parametrize(
    "cognito_client_stub",
    [
        {
            "method": "initiate_auth",
            "response": {"AuthenticationResult": {}},
            "method_args": {
                "AuthFlow": "USER_PASSWORD_AUTH",
                "ClientId": "1234567890abcdef",
                "AuthParameters": {"USERNAME": "testuser", "PASSWORD": "testpassword"},
            },
        }
    ],
    indirect=True,
)
def test_authenticate_exception(
    cognito_client_stub, authenticator_args: dict[str, str]
):
    with pytest.raises(KeyError):
        authenticator = CognitoAuthenticator(**authenticator_args)
        authenticator.authenticate("testuser", "testpassword")


@pytest.mark.parametrize(
    "cognito_client_stub",
    [
        {
            "method": "initiate_auth",
            "response": {
                "AuthenticationResult": {
                    "AccessToken": "mock_access_token",
                    "IdToken": "mock_id_token",
                    "ExpiresIn": 3600,
                    "TokenType": "Bearer",
                }
            },
            "method_args": {
                "AuthFlow": "REFRESH_TOKEN_AUTH",
                "ClientId": "1234567890abcdef",
                "AuthParameters": {"REFRESH_TOKEN": "mock_refresh_token"},
            },
        }
    ],
    indirect=True,
)
def test_refresh_tokens(
    cognito_client_stub,
    mock_access_token: str,
    mock_refresh_token: str,
    mock_id_token: str,
):
    region = "eu-west-1"
    client_id = "1234567890abcdef"

    authenticator = CognitoAuthenticator(region, client_id)
    tokens = authenticator.refresh_tokens(mock_refresh_token)

    assert tokens == {
        "access_token": mock_access_token,
        "id_token": mock_id_token,
        "expires_in": 3600,
    }


@pytest.mark.parametrize(
    "cognito_client_exception_stub, error",
    [
        (
            {
                "method": "initiate_auth",
                "code": "ClientError",
                "message": "Unknown Error",
            },
            "Token refresh failed: Unknown Error",
        ),
    ],
    indirect=["cognito_client_exception_stub"],
)
def test_refresh_tokens_exceptions(
    cognito_client_exception_stub, error: str, mock_access_token: str
):
    """Test the authenticate method of CognitoAuthenticator."""
    region = "eu-west-1"
    client_id = "1234567890abcdef"

    with pytest.raises(Exception) as excinfo:
        authenticator = CognitoAuthenticator(region, client_id)
        authenticator.refresh_tokens(mock_access_token)
    assert error == str(excinfo.value)
