from datetime import datetime
from typing import Any, Dict

import boto3
import jwt
from botocore.exceptions import ClientError


class CognitoToken:
    """
    A set of Cognito tokens.

    Args:
        access_token: Access token.
        refresh_token: Refresh token.
        id_token: ID token.
    """

    def __init__(
        self,
        access_token: str,
        refresh_token: str,
        id_token: str,
    ) -> None:
        self.access_token = access_token
        self.id_token = id_token
        self.refresh_token = refresh_token

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, CognitoToken)
            and other.access_token == self.access_token
            and other.id_token == self.id_token
            and other.refresh_token == self.refresh_token
        )

    def __hash__(self) -> int:
        return hash((self.access_token, self.id_token, self.refresh_token))

    @property
    def decoded_payload(self) -> Dict:
        """Decode and cache the JWT token payload"""
        # Decode without verification since we just want the payload.
        # Verification just means we check where the token came from.
        return jwt.decode(self.access_token, options={"verify_signature": False})

    @property
    def user_sub_id(self) -> str:
        """Get user ID from token"""
        try:
            return self.decoded_payload["sub"]
        except KeyError:
            raise KeyError("Invalid token: 'sub' key not found in payload")

    @property
    def username(self) -> str:
        """Get username from token"""
        try:
            return self.decoded_payload["username"]
        except KeyError:
            raise KeyError("Invalid token: 'username' key not found in payload")

    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        try:
            exp = self.decoded_payload["exp"]
        except KeyError:
            raise KeyError("Invalid token: Token did not include an expiry time")
        exp_datetime = datetime.fromtimestamp(exp)
        return datetime.now() > exp_datetime


class CognitoAuthenticator:
    """A class to authenticate users with Amazon Cognito and retrieve access tokens.

    This class handles the authentication of users with Amazon Cognito, allowing them
    to retrieve access tokens by providing their username and password.

    The authentication process includes:
    1. Initializing a connection to the Cognito Identity Provider
    2. Authenticating the user with their username and password
    3. Retrieving and returning the access token (and optionally refresh and ID tokens)

    Args:
        region: Amazon Web Services region where the Cognito User Pool resides.
        client_id: Cognito User Pool Application Client ID.
    """

    def __init__(self, region: str, client_id: str) -> None:
        self.region = region
        self.client_id = client_id

        # Initialize Cognito client
        self.client = boto3.client("cognito-idp", region_name=self.region)

    def authenticate(self, username: str, password: str) -> CognitoToken:
        """Authenticate with Cognito and retrieve tokens.

        Args:
            username: str: The username of the user. This can be an email or Cognito username.
            password: str: The password of the user

        Returns:
            Cognito tokens.

        Raises:
            Exception: If authentication fails due to invalid credentials or other errors
        """

        try:
            # Initiate authentication with Cognito
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )

            # Cognito can issue challenges in a number of situations, including
            # trying to authenticate with a temporary password that needs to be
            # replaced. We could handle that challenge in here one day, but for
            # now we'll print the details and you'll need to respond manually
            # via the AWS CLI.
            if response.get("ChallengeName"):
                raise Exception(f"Authentication was challenged: {response}")

            result = response["AuthenticationResult"]

            return CognitoToken(
                self.get_cognito_response_value(result, "AccessToken"),
                self.get_cognito_response_value(result, "RefreshToken"),
                self.get_cognito_response_value(result, "IdToken"),
            )

        except self.client.exceptions.NotAuthorizedException:
            raise Exception("Invalid username or password.")
        except self.client.exceptions.UserNotFoundException:
            raise Exception("User not found.")
        except self.client.exceptions.PasswordResetRequiredException:
            raise Exception("Password reset required.")
        except self.client.exceptions.UserNotConfirmedException:
            raise Exception("User account is not verified.")
        except ClientError as e:
            error_message = e.response.get("Error", {}).get("Message")
            raise Exception(f"Authentication failed: {error_message}")
        except Exception:
            raise

    @staticmethod
    def get_cognito_response_value(response: Any, key: str) -> str:
        """
        Gets a specific value from a dictionary provided by Cognito.

        Args:
            response: Cognito response.
            key: Value key.

        Returns:
            Response value.

        Raises:
            KeyError: Raised if the specified value is not present.
        """

        if value := response.get(key):
            return str(value)

        raise KeyError(f"Cognito did not provide {key}")

    def refresh_tokens(self, refresh_token: str) -> CognitoToken:
        """Refresh tokens using a refresh token.

        Args:
            refresh_token (str): The refresh token to use

        Returns:
            Refreshed tokens.

        Raises:
            Exception: If token refresh fails
        """
        try:
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
            )

            auth_result = response.get("AuthenticationResult", {})

            return CognitoToken(
                self.get_cognito_response_value(auth_result, "AccessToken"),
                # The original code before I refactored this intentionally kept
                # the same refresh token.
                refresh_token,
                self.get_cognito_response_value(auth_result, "IdToken"),
            )

        except ClientError as e:
            error_message = e.response.get("Error", {}).get("Message", "Unknown error")
            raise Exception(f"Token refresh failed: {error_message}")
