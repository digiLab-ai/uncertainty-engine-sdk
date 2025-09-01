from uncertainty_engine_resource_client.api.auth_api import AuthApi
from uncertainty_engine_resource_client.api_client import ApiClient
from uncertainty_engine_resource_client.configuration import Configuration
from uncertainty_engine_resource_client.models.token_response import TokenResponse

from uncertainty_engine.api_providers import ApiProviderBase
from uncertainty_engine.auth_service import AuthService


class AuthProvider(ApiProviderBase):
    """
    Client for interacting with the Resource Service's authorisation endpoints.

    Args:
        auth_service: Authorisation service.
        deployment: API endpoint.
    """

    def __init__(self, auth_service: AuthService, api_endpoint: str) -> None:
        super().__init__(api_endpoint, auth_service)

        self.client = ApiClient(configuration=Configuration(host=api_endpoint))
        self.auth_client = AuthApi(self.client)

        self.update_api_authentication()

    @ApiProviderBase.with_auth_refresh
    def get_tokens(self) -> TokenResponse:
        """
        Gets a set of Resource Service tokens.
        """

        return self.auth_client.get_tokens()

    def update_api_authentication(self) -> None:
        """
        Updates the client's authorisation and identity headers.
        """

        if not self.auth_service.token:
            return

        headers = self.auth_service.get_auth_header(include_id=True)
        self.client.default_headers.update(headers)
