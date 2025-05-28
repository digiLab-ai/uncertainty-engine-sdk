from typing import Iterator
from unittest.mock import Mock, patch

from pytest import fixture

from uncertainty_engine.api_invoker import LiveApiInvoker


@fixture
def api() -> LiveApiInvoker:
    return LiveApiInvoker("https://test-api")


@fixture
def req() -> Iterator[Mock]:
    response = Mock()
    response.json = Mock(return_value={"foo": "bar"})

    target = "uncertainty_engine.api_invoker.request"

    with patch(target, return_value=response) as patched_request:
        yield patched_request


def test_deserialize(api: LiveApiInvoker, req: Mock) -> None:
    assert api.get("/foo") == {"foo": "bar"}


def test_get(api: LiveApiInvoker, req: Mock) -> None:
    api.get("/foo")
    req.assert_called_once_with("GET", "https://test-api/foo")


def test_post(api: LiveApiInvoker, req: Mock) -> None:
    api.post(
        "/foo",
        {"greeting": "hello"},
    )

    req.assert_called_once_with(
        "POST",
        "https://test-api/foo",
        json={"greeting": "hello"},
    )
