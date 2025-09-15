import json
import os
from pathlib import Path
from typing import Optional
from warnings import warn

import jwt

from uncertainty_engine.cognito_authenticator import CognitoAuthenticator, CognitoToken
from uncertainty_engine.types import GetResourceToken

AUTH_CACHE_ID_TOKEN = "id_token"
"""
Key for the user's ID token in the authorisation cache file.
"""

AUTH_CACHE_RESOURCE_TOKEN = "resource_token"
"""
Key for the user's resource token in the authorisation cache file.
"""

AUTH_CACHE_KEYS = [
    AUTH_CACHE_ID_TOKEN,
    AUTH_CACHE_RESOURCE_TOKEN,
    "account_id",
    "access_token",
    "refresh_token",
]
"""
All the keys that are expected to exist in the authorisation cache file.
"""

AUTH_FILE_NAME = ".ue_auth"


class AuthService:
    """
    Manages API authorisation, including authentication, tokens and HTTP
    headers.

    Args:
        authenticator: Cognito authenticator.
        get_resource_token: Callback to request a Resource Service API
            token.
    """

    def __init__(
        self,
        authenticator: CognitoAuthenticator,
        get_resource_token: GetResourceToken,
    ) -> None:
        self._get_resource_token = get_resource_token
        self.account_id: Optional[str] = None
        self.token: Optional[CognitoToken] = None
        self.authenticator = authenticator

        self.resource_token: str | None = None
        """
        Resource Service API token.
        """

        # Load auth details, if not found they will remain None
        self._load_from_file()

    def authenticate(self, account_id: str | None = None) -> None:
        """
        Set authentication credentials.

        Args:
            account_id : **DEPRECATED** This parameter is no longer used
                and will be removed in the next release. Defaults to
                `None`. The account ID is now obtained from HTTP
                headers.
        """
        # TODO: The following can be removed once `account_id` argument
        # is removed.
        if account_id is not None:
            warn(
                "The 'account_id' parameter is deprecated and will be removed in the next "
                "release. Fetching account ID from HTTP headers instead.",
                DeprecationWarning,
                # The stack level is set to 3 so that when it is called
                # via the `Client` the deprecation warning will still
                # show.
                stacklevel=3,
            )

        # Load username + password from .env or take inputs
        username = os.getenv("UE_USERNAME")
        password = os.getenv("UE_PASSWORD")

        if not username or not password:
            raise ValueError(
                "Username and password must be provided or set in environment variables UE_USERNAME and UE_PASSWORD"
            )

        self.token = self.authenticator.authenticate(username, password)

        # Get a new resource token only if we didn't load one already
        # from the cache.
        self.resource_token = self.resource_token or self._get_resource_token()

        # Get the account ID from the resource token if it is not
        # already set.
        self.account_id = self.account_id or self._get_account_id(self.resource_token)

        # Save tokens to AUTH_FILE_NAME in the user's home directory
        self._save_to_file()

    @property
    def is_authenticated(self) -> bool:
        """
        Check if authentication has been performed

        Returns:
            ``True`` if authenticated, ``False`` otherwise.
        """
        return all(
            [
                self.token is not None,
                self.account_id is not None,
            ]
        )

    @property
    def auth_file_path(self) -> Path:
        """Get the path to the auth file"""
        return Path.home() / AUTH_FILE_NAME

    def clear(self) -> None:
        """Clear authentication state"""
        self.token = None
        auth_file = self.auth_file_path
        if auth_file.exists():
            auth_file.unlink()

    def _save_to_file(self) -> None:
        """Save authentication details to a file"""

        if not self.is_authenticated:
            raise Exception(
                "Must be authenticated before saving authentication details."
            )

        auth_data = {
            AUTH_CACHE_ID_TOKEN: self.token.id_token,
            AUTH_CACHE_RESOURCE_TOKEN: self.resource_token,
            "account_id": self.account_id,
            "access_token": self.token.access_token,
            "refresh_token": self.token.refresh_token,
        }

        with open(self.auth_file_path, "w") as f:
            json.dump(auth_data, f)

        # Set file permissions (owner read/write only - 0600)
        os.chmod(self.auth_file_path, 0o600)

    @staticmethod
    def _get_account_id(resource_token: str) -> str:
        """
        Gets the user's account ID by decoding the resource token.

        Args:
            resource_token: The resource token to decode.

        Raises:
            ValueError: If JWT is unable to decode the token or if the
                account ID cannot be found in the decoded token.
        """
        try:
            decoded_token = jwt.decode(
                resource_token,
                options={
                    "verify_signature": False,
                },
            )

            return decoded_token["account_id"]
        except jwt.DecodeError as e:
            raise ValueError(f"Failed to decode token: {e}")
        except KeyError:
            raise ValueError("Unable to find 'account_id' in decoded token.")

    def refresh(self) -> CognitoToken:
        """
        Refresh the access token

        Returns
            A Cognito Token containing the user's new access token.

        """
        if not self.token or not self.token.refresh_token:
            raise ValueError("No refresh token available. Please authenticate first.")
        try:
            self.token = self.authenticator.refresh_tokens(
                self.token.refresh_token,
            )
            self._save_to_file()
            return self.token
        except Exception as e:
            self.clear()
            raise ValueError(f"Failed to refresh token: {str(e)}")

    def get_auth_header(
        self,
        include_id: bool = False,
    ) -> dict[str, str]:
        """
        Gets the authorisation and identity headers to include in an API request.

        If the resource token is present it will be passed as the
        "X-Resource-Service-Token", otherwise the access token will be passed instead.

        Args:
            include_id: Include an ID token as the "X-ID-Token" header.

        Returns:
            HTTP request headers.
        """
        if not self.token:
            raise ValueError("Not authenticated")

        headers = {
            "Authorization": f"Bearer {self.token.access_token}",
            "X-Resource-Service-Token": self.resource_token or self.token.access_token,
        }

        if include_id:
            headers["X-ID-Token"] = self.token.id_token

        return headers

    def _load_from_file(self) -> None:
        """Load authentication details from file if it exists"""
        auth_file = self.auth_file_path
        if not auth_file.exists():
            self.token = None
            return

        try:
            with open(auth_file, "r") as f:
                auth_data = json.load(f)
            if all(k in auth_data for k in AUTH_CACHE_KEYS):
                self.token = CognitoToken(
                    access_token=auth_data["access_token"],
                    refresh_token=auth_data["refresh_token"],
                    id_token=auth_data[AUTH_CACHE_ID_TOKEN],
                )
                self.account_id = auth_data["account_id"]
                self.resource_token = auth_data[AUTH_CACHE_RESOURCE_TOKEN]
        except Exception as e:
            raise Exception(
                f"Error loading authentication details: {str(e)}. Please ensure you are authenticated."
            )
