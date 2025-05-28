from pytest import fixture, raises

from tests.mock_api_invoker import MockApiInvoker


@fixture
def api() -> MockApiInvoker:
    return MockApiInvoker()


def test_expect_get__one(api: MockApiInvoker) -> None:
    api.expect_get("/foo", "bar")
    result = api.get("/foo")
    assert result == "bar"


def test_expect_get__two(api: MockApiInvoker) -> None:
    api.expect_get("/foo", "0", "1")

    result_0 = api.get("/foo")
    result_1 = api.get("/foo")

    assert result_0 == "0"
    assert result_1 == "1"


def test_expect_get__unexpected_method(api: MockApiInvoker) -> None:
    api.expect_get("/foo", "bar")

    with raises(AssertionError) as ex:
        api.post("/foo", body=None)

    assert str(ex.value) == "Expected method GET but encountered POST"


def test_expect_get__unexpected_path(api: MockApiInvoker) -> None:
    api.expect_get("/foo", "bar")

    with raises(AssertionError) as ex:
        api.get("/woo")

    assert str(ex.value) == "Expected path /foo but encountered /woo"


def test_expect_post(api: MockApiInvoker) -> None:
    api.expect_post("/foo", expect_body="body", response="bar")
    result = api.post("/foo", "body")
    assert result == "bar"


def test_expect_post__no_body_expectation(api: MockApiInvoker) -> None:
    api.expect_post("/foo", response="bar")
    result = api.post("/foo", "body")
    assert result == "bar"


def test_expect_post__unexpected_body(api: MockApiInvoker) -> None:
    api.expect_post("/foo", expect_body="bob", response="bar")

    with raises(AssertionError) as ex:
        api.post("/foo", "bobby")

    assert str(ex.value) == "Expected body bob but encountered bobby"


def test_unexpected(api: MockApiInvoker) -> None:
    with raises(AssertionError) as ex:
        api.get("/foo")

    assert str(ex.value) == "Did not expect call #0 (GET on /foo)"
