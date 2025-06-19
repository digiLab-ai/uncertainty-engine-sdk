from contextlib import contextmanager
from typing import Any, Iterator

from pytest import MonkeyPatch

from uncertainty_engine.api_invoker import ApiInvoker
from uncertainty_engine.client import Client


class MockApiInvoker(ApiInvoker):
    """
    An implementation of `ApiInvoker` to aid unit testing.
    """

    def __init__(self) -> None:
        self._expect_bodies: list[Any | None] = []
        self._expect_methods: list[str] = []
        self._expect_paths: list[str] = []
        self._next_expectation_index = 0
        self._responses: list[Any] = []

    def _add_expectation(
        self,
        expect_method: str,
        expect_path: str,
        expect_body: Any | None,
        response: Any | None,
    ) -> None:
        """
        Appends an expectation of an API request.

        Args:
            expect_method: HTTP method to expect.
            expect_path: Path to expect.
            expect_body: Optional body to expect.
            response: Response to return.
        """

        self._expect_methods.append(expect_method)
        self._expect_paths.append(expect_path)
        self._expect_bodies.append(expect_body)
        self._responses.append(response)

    def _invoke(
        self,
        method: str,
        path: str,
        body: Any | None = None,
    ) -> Any:
        """
        Mocks an invocation of the API and asserts that it was expected.

        Args:
            method: HTTP method.
            path: API path.
            body: Optional body.

        Returns:
            Mocked response.
        """

        if self._next_expectation_index >= len(self._expect_methods):
            assert (
                False
            ), f"Did not expect call #{self._next_expectation_index} ({method} on {path})"

        expect_method = self._expect_methods[self._next_expectation_index]
        assert (
            method == expect_method
        ), f"Expected method {expect_method} but encountered {method}"

        expect_path = self._expect_paths[self._next_expectation_index]
        assert (
            path == expect_path
        ), f"Expected path {expect_path} but encountered {path}"

        if expect_body := self._expect_bodies[self._next_expectation_index]:
            assert (
                body == expect_body
            ), f"Expected body {expect_body} but encountered {body}"

        response = self._responses[self._next_expectation_index]
        self._next_expectation_index += 1
        return response

    def expect_get(self, expect_path: str, *response: Any) -> None:
        """
        Appends an expectation of a GET request.

        Args:
            expect_path: Path to expect.
            response: Responses to return.
        """

        for r in response:
            self._add_expectation(
                "GET",
                expect_path,
                None,
                r,
            )

    def expect_post(
        self,
        expect_path: str,
        expect_body: Any | None = None,
        response: Any | None = None,
    ) -> None:
        """
        Appends an expectation of a POST request.

        Args:
            expect_path: Path to expect.
            expect_body: Optional body to expect.
            response: Response to return.
        """

        self._add_expectation(
            "POST",
            expect_path,
            expect_body,
            response,
        )


@contextmanager
def mock_core_api(client: Client) -> Iterator[MockApiInvoker]:
    """
    Patches and yields a mock invoker for the Core API.

    Args:
        client: Client to patch.

    Yields:
        Mock invoker for the Core API.
    """

    original_invoker = client.core_api
    mock_invoker = MockApiInvoker()
    client.core_api = mock_invoker

    with MonkeyPatch.context() as mp:
        mp.setenv("UE_USERNAME", "user@uncertaintyengine.ai")

        try:
            yield mock_invoker
        finally:
            client.core_api = original_invoker
