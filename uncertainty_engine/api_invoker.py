from abc import ABC, abstractmethod
from typing import Any

from requests import request

from uncertainty_engine.auth_service import AuthService


class ApiInvoker(ABC):
    """
    Base implementation of an API invoker.
    """

    @abstractmethod
    def _invoke(
        self,
        method: str,
        path: str,
        body: Any | None = None,
    ) -> Any:
        """
        Invoke the API.

        Args:
            method: HTTP method.
            path: API path.
            body: Optional body.

        Returns:
            API response.
        """

    def get(self, path: str) -> Any:
        """
        Invoke a GET request.

        Args:
            path: API path.

        Returns:
            API response.
        """

        return self._invoke(
            "GET",
            path,
        )

    def post(self, path: str, body: Any) -> Any:
        """
        Invoke a POST request.

        Args:
            path: API path.
            body: Request body.

        Returns:
            API response.
        """

        return self._invoke(
            "POST",
            path,
            body=body,
        )


class HttpApiInvoker(ApiInvoker):
    """
    An implementation of `ApiInvoker` for HTTP APIs.

    Args:
        auth_service: Authorisation service.
        endpoint: API endpoint. Must start with a protocol (i.e. "https://") and
            must not end with a slash.
    """

    def __init__(self, auth_service: AuthService, endpoint: str) -> None:
        self._auth_service = auth_service
        self._endpoint = endpoint

    def _invoke(
        self,
        method: str,
        path: str,
        body: Any | None = None,
    ) -> Any:
        """
        Invoke the API.

        Args:
            method: HTTP method.
            path: API path.
            body: Optional body.

        Returns:
            API response.
        """

        url = self._endpoint + path

        kwargs = {
            "headers": {
                **self._auth_service.get_auth_header(),
            },
        }

        if body:
            kwargs["json"] = body

        has_refreshed_token = False

        while True:
            response = request(
                method,
                url,
                **kwargs,  # type: ignore
            )

            if 200 <= response.status_code < 300:
                return response.json()

            if has_refreshed_token:
                # If we've already refreshed the authorisation token then the
                # problem is probably unrelated, so don't try again.
                response.raise_for_status()
                return

            # Re-authenticate.
            self._auth_service.refresh()

            # Update the authorisation header.
            kwargs["headers"] = {
                **kwargs["headers"],
                **self._auth_service.get_auth_header(),
            }

            # Remember that we've refreshed the token in case the next
            # attempt fails too.
            has_refreshed_token = True
