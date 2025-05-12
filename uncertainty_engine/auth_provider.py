import json
import os
from pathlib import Path

from uncertainty_engine.cognito_provider import (
    CognitoAuthenticator,
    get_cognito_authenticator,
)
from pydantic import BaseModel

AUTH_FILE_NAME = ".ue_auth"


class AuthDetails(BaseModel):
    account_id: str
    access_token: str
    refresh_token: str


class AuthProvider:
    """Authentication state management"""

    def __init__(self):
        self.account_id: str = None
        self.access_token: str = None
        self.refresh_token: str = None
        self.cognito_authenticator: CognitoAuthenticator = get_cognito_authenticator()

    def authenticate(self, account_id: str) -> AuthDetails:
        """Set authentication credentials"""
        self.account_id = account_id

        auth_details = self.cognito_authenticator.authenticate()
        self.access_token = auth_details["access_token"]
        self.refresh_token = auth_details["refresh_token"]

        auth_details["account_id"] = self.account_id

        return AuthDetails.model_validate(auth_details)

    def _get_auth_file_path(self) -> Path:
        """Get the path to the auth file in the user's home directory"""
        return Path.home() / self.AUTH_FILE_NAME

    def _save_auth_details(self) -> None:
        """Save authentication details to a file with secure permissions"""
        if not self.is_authenticated:
            return

        auth_data = {
            "account_id": self.account_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }

        auth_file = self._get_auth_file_path()

        # Write to file
        with open(auth_file, "w") as f:
            json.dump(auth_data, f)

        # Set secure permissions (owner read/write only - 0600)
        os.chmod(auth_file, 0o600)

    def _load_auth_details(self) -> bool:
        """Load authentication details from file if it exists"""
        auth_file = self._get_auth_file_path()

        if not auth_file.exists():
            return False

        try:
            with open(auth_file, "r") as f:
                auth_data = json.load(f)

            self.account_id = auth_data.get("account_id")
            self.access_token = auth_data.get("access_token")
            self.refresh_token = auth_data.get("refresh_token")

            return self.is_authenticated
        except (json.JSONDecodeError, IOError):
            # Handle file read or parse errors
            return False

    def clear_auth(self) -> None:
        """Clear authentication credentials and remove auth file"""
        self.account_id = None
        self.access_token = None
        self.refresh_token = None

        auth_file = self._get_auth_file_path()
        if auth_file.exists():
            auth_file.unlink()

    @property
    def is_authenticated(self) -> bool:
        """Check if authentication has been performed"""
        return all([self.access_token, self.account_id, self.refresh_token]) is not None
