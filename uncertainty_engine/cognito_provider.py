import os
import boto3
from datetime import datetime
from typing import Dict, Optional, Tuple
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field


class CognitoAuthenticator:
    """A class to authenticate users with Amazon Cognito and retrieve access tokens.

    This class handles the authentication of users with Amazon Cognito, allowing them
    to retrieve access tokens by providing their username and password. It supports
    loading credentials from environment variables or a .env file.

    The authentication process includes:
    1. Initializing a connection to the Cognito Identity Provider
    2. Authenticating the user with their username and password
    3. Retrieving and returning the access token (and optionally refresh and ID tokens)

    Attributes:
        region (str): AWS region where the Cognito user pool is located
        user_pool_id (str): ID of the Cognito user pool
        client_id (str): ID of the client application
        username (str, optional): Username for authentication
        password (str, optional): Password for authentication
        client (boto3.client): Boto3 client for Cognito Identity Provider
    """

    def __init__(
        self,
        region: str,
        user_pool_id: str,
        client_id: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        env_file: Optional[str] = None,
    ):
        """Initialize the CognitoAuthenticator with AWS Cognito configuration.

        Args:
            region (str): AWS region where the Cognito user pool is located (e.g., 'us-east-1')
            user_pool_id (str): The unique identifier of your Cognito user pool
            client_id (str): The client ID (app client ID) from your Cognito user pool
            username (str, optional): Username for authentication. Defaults to None.
            password (str, optional): Password for authentication. Defaults to None.
            env_file (str, optional): Path to .env file to load credentials from. Defaults to None.

        If username and password are not provided, they will be loaded from environment variables
        or the specified .env file.
        """
        self.region = region
        self.user_pool_id = user_pool_id
        self.client_id = client_id

        # Load credentials from .env file if specified
        if env_file:
            load_dotenv(env_file)

        # Use provided credentials or load from environment
        self.username = username or os.getenv("COGNITO_USERNAME")
        self.password = password or os.getenv("COGNITO_PASSWORD")

        # Initialize Cognito client
        self.client = boto3.client("cognito-idp", region_name=self.region)

    def authenticate(self) -> dict[str, str]:
        """Authenticate with Cognito and retrieve tokens.

        Returns:
            Dict: A dictionary containing the access token, refresh token, and ID token

        Raises:
            Exception: If authentication fails due to invalid credentials or other errors
        """
        if not self.username or not self.password:
            raise Exception(
                "Username and password are required for authentication",
            )

        try:
            # Initiate authentication with Cognito
            response = self.client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": self.username, "PASSWORD": self.password},
            )

            # Extract authentication result
            access_token = response["AuthenticationResult"]["AccessToken"]
            refresh_token = response["AuthenticationResult"]["RefreshToken"]

            return {"access_token": access_token, "refresh_token": refresh_token}

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            error_message = e.response.get("Error", {}).get("Message")

            if error_code == "NotAuthorizedException":
                raise Exception("Invalid username or password")
            elif error_code == "UserNotFoundException":
                raise Exception("User not found")
            elif error_code == "UserNotConfirmedException":
                raise Exception("User is not confirmed")
            else:
                raise Exception(f"Authentication failed: {error_message}")
        except Exception:
            raise

    def get_access_token(self) -> str:
        """Get only the access token from Cognito.

        A convenience method to get just the access token.

        Returns:
            str: The access token

        Raises:
            Exception: If authentication fails
        """
        auth_result = self.authenticate()
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
            error_message = e.response.get("Error", {}).get("Message")
            raise Exception(f"Token refresh failed: {error_message}")


def get_cognito_authenticator(
    region: str = None,
    user_pool_id: str = None,
    client_id: str = None,
    env_file: str = ".env",
) -> CognitoAuthenticator:
    """Create a CognitoAuthenticator instance using environment variables or provided values.

    Args:
        region (str, optional): AWS region. Defaults to value from environment.
        user_pool_id (str, optional): Cognito user pool ID. Defaults to value from environment.
        client_id (str, optional): Cognito client ID. Defaults to value from environment.
        env_file (str, optional): Path to .env file. Defaults to ".env".

    Returns:
        CognitoAuthenticator: Configured authenticator instance
    """
    # Load environment variables if they exist
    load_dotenv(env_file)

    # Use provided values or environment variables
    region = region or os.getenv("COGNITO_REGION")
    user_pool_id = user_pool_id or os.getenv("COGNITO_USER_POOL_ID")
    client_id = client_id or os.getenv("COGNITO_CLIENT_ID")

    if not all([region, user_pool_id, client_id]):
        raise ValueError(
            "Missing required configuration. Provide region, user_pool_id, and client_id "
            "either as parameters or in your environment variables."
        )

    return CognitoAuthenticator(
        region=region, user_pool_id=user_pool_id, client_id=client_id, env_file=env_file
    )
