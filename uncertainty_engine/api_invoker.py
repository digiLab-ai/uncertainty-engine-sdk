from abc import ABC, abstractmethod
from typing import Any

from requests import request


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

        ...

    def get(self, path: str) -> Any:
        """
        Invoke a GET request.

        Args:
            path: API path.

        Returns:
            API response.
        """

        return self._invoke("GET", path)

    def post(self, path: str, body: Any) -> Any:
        """
        Invoke a POST request.

        Args:
            path: API path.
            body: Request body.

        Returns:
            API response.
        """

        return self._invoke("POST", path, body=body)


class LiveApiInvoker(ApiInvoker):
    """
    An implementation of `ApiInvoker` for live API calls.

    Args:
        endpoint: API endpoint. Must start with a protocol (i.e. "https://") and
            must not end with a slash.
    """

    def __init__(self, endpoint: str) -> None:
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

        return request(
            method,
            self._endpoint + path,
            json=body,
        ).json()
