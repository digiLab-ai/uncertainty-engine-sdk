from pytest import raises

from tests.mock_api_invoker import mock_core_api
from uncertainty_engine.client import Client


def test_expect_get__one(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_get("/foo", "bar")

        result = client.core_api.get("/foo")

    assert result == "bar"


def test_expect_get__two(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_get("/foo", "0", "1")

        result_0 = client.core_api.get("/foo")
        result_1 = client.core_api.get("/foo")

    assert result_0 == "0"
    assert result_1 == "1"


def test_expect_get__unexpected_method(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_get("/foo", "bar")

        with raises(AssertionError) as ex:
            client.core_api.post("/foo", body=None)

    assert str(ex.value) == "Expected method GET but encountered POST"


def test_expect_get__unexpected_path(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_get("/foo", "bar")

        with raises(AssertionError) as ex:
            client.core_api.get("/woo")

    assert str(ex.value) == "Expected path /foo but encountered /woo"


def test_expect_post(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_post("/foo", expect_body="body", response="bar")

        result = client.core_api.post("/foo", "body")

    assert result == "bar"


def test_expect_post__no_body_expectation(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_post("/foo", response="bar")

        result = client.core_api.post("/foo", "body")

    assert result == "bar"


def test_expect_post__unexpected_body(client: Client) -> None:
    with mock_core_api(client) as api:
        api.expect_post("/foo", expect_body="bob", response="bar")

        with raises(AssertionError) as ex:
            client.core_api.post("/foo", "bobby")

    assert str(ex.value) == "Expected body bob but encountered bobby"


def test_unexpected(client: Client) -> None:
    with mock_core_api(client):
        with raises(AssertionError) as ex:
            client.core_api.get("/foo")

    assert str(ex.value) == "Did not expect call #0 (GET on /foo)"
