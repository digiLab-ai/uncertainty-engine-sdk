from datetime import datetime
from typing import Dict

import boto3
import jwt
from botocore.exceptions import ClientError


class CognitoToken:
    """
    Wrapper around authentication tokens with decoding capabilities

    Attributes:
        access_token (str): The access token for the user
        refresh_token (str): The refresh token for the user
        _decoded_payload (dict): The decoded payload of the JWT token

    """

    def __init__(self, access_token: str, refresh_token: str):
        self.access_token = access_token
        self.refresh_token = refresh_token

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

    Attributes:
        region (str): AWS region where the Cognito user pool is located
        client_id (str): ID of the client application
        client (boto3.client): Boto3 client for Cognito Identity Provider
    """

    def __init__(
        self,
        region: str,
        client_id: str,
    ):
        """Initialize the CognitoAuthenticator with AWS Cognito configuration.

        Args:
            region (str): AWS region where the Cognito user pool is located (e.g., 'us-east-1')
            client_id (str): The client ID (app client ID) from your Cognito user pool

        """
        self.region = region
        self.client_id = client_id

        # Initialize Cognito client
        self.client = boto3.client("cognito-idp", region_name=self.region)

    def authenticate(self, username: str, password: str) -> dict[str, str]:
        """Authenticate with Cognito and retrieve tokens.

        Args:
            username: str: The username of the user. This can be an email or Cognito username.
            password: str: The password of the user

        Returns:
            Dict: A dictionary containing the access token, refresh token, and ID token

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

            # Extract authentication result
            access_token = response["AuthenticationResult"]["AccessToken"]
            refresh_token = response["AuthenticationResult"]["RefreshToken"]

            return {"access_token": access_token, "refresh_token": refresh_token}
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

    def get_access_token(self, username: str, password: str) -> str:
        """Get only the access token from Cognito.

        A convenience method to get just the access token.

        Returns:
            str: The access token

        Raises:
            Exception: If authentication fails
        """
        auth_result = self.authenticate(username, password)
        return auth_result.get("access_token")

    def refresh_tokens(self, refresh_token: str) -> Dict:
        """Refresh tokens using a refresh token.

        Args:
            refresh_token (str): The refresh token to use

        Returns:
            Dict: A dictionary containing the new access token and ID token

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

            return {
                "access_token": auth_result.get("AccessToken"),
                "id_token": auth_result.get("IdToken"),
                "expires_in": auth_result.get("ExpiresIn", 3600),
            }

        except ClientError as e:
            error_message = e.response.get("Error", {}).get("Message", "Unknown error")
            raise Exception(f"Token refresh failed: {error_message}")
