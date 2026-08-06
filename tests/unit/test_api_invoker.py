from typing import Iterator
from unittest.mock import Mock, PropertyMock, call, patch

from pytest import fixture, raises

from uncertainty_engine.api_invoker import HttpApiInvoker

REQUEST_TARGET = "uncertainty_engine.api_invoker.request"


@fixture
def api(auth_service: Mock) -> HttpApiInvoker:
    return HttpApiInvoker(auth_service, "https://test-api")


@fixture
def auth_service() -> Mock:
    service = Mock()

    service.get_auth_header = Mock(
        side_effect=[
            {
                "Authorisation": "Bearer FOO",
            },
            {
                "Authorisation": "Bearer BAR",
            },
        ],
    )

    return service


@fixture
def req() -> Iterator[Mock]:
    response = Mock()
    response.status_code = 200
    response.json = Mock(return_value={"foo": "bar"})

    with patch(REQUEST_TARGET, return_value=response) as patched_request:
        yield patched_request


def test_deserialize(api: HttpApiInvoker, req: Mock) -> None:
    assert api.get("/foo") == {"foo": "bar"}


def test_get(api: HttpApiInvoker, req: Mock) -> None:
    api.get("/foo")

    req.assert_called_once_with(
        "GET",
        "https://test-api/foo",
        headers={
            "Authorisation": "Bearer FOO",
        },
    )


def test_get_with_one_failure(api: HttpApiInvoker) -> None:
    response = Mock()
    type(response).status_code = PropertyMock(side_effect=[401, 200])

    with patch(REQUEST_TARGET, return_value=response) as request:
        api.get("/foo")

        request.assert_has_calls(
            [
                call(
                    "GET",
                    "https://test-api/foo",
                    headers={
                        "Authorisation": "Bearer FOO",
                    },
                ),
                call(
                    "GET",
                    "https://test-api/foo",
                    headers={
                        "Authorisation": "Bearer BAR",
                    },
                ),
            ]
        )


def test_get_with_two_failures(api: HttpApiInvoker) -> None:
    response = Mock()
    response.raise_for_status = Mock(side_effect=Exception("raised for status"))
    type(response).status_code = PropertyMock(side_effect=[401, 401])

    with patch(REQUEST_TARGET, return_value=response):
        with raises(Exception) as ex:
            api.get("/foo")

    assert str(ex.value) == "raised for status"


def test_get_with_non_auth_failure_does_not_refresh(
    api: HttpApiInvoker,
    auth_service: Mock,
) -> None:
    """
    A non-authorisation failure (e.g. a transient 5xx) raises
    immediately without refreshing the token.
    """
    response = Mock()
    response.raise_for_status = Mock(
        side_effect=Exception("raised for status"),
    )

    type(response).status_code = PropertyMock(side_effect=[500])

    with patch(REQUEST_TARGET, return_value=response) as request:
        with raises(Exception) as ex:
            api.get("/foo")

    assert str(ex.value) == "raised for status"
    assert request.call_count == 1
    auth_service.refresh.assert_not_called()


def test_post(api: HttpApiInvoker, req: Mock) -> None:
    api.post(
        "/foo",
        {"greeting": "hello"},
    )

    req.assert_called_once_with(
        "POST",
        "https://test-api/foo",
        headers={
            "Authorisation": "Bearer FOO",
        },
        json={"greeting": "hello"},
    )
