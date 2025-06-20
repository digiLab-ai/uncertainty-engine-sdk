from pytest import raises

from uncertainty_engine import Environment


def test_get() -> None:
    env = Environment.get("dev")

    assert env == Environment(
        cognito_user_pool_client_id="3n437fei4uhp4ouj8b4mmt09l9",
        core_api="https://rqreuca5q9.execute-api.eu-west-2.amazonaws.com",
        region="eu-west-2",
        resource_api="https://ajn7f4an9j.execute-api.eu-west-2.amazonaws.com",
    )


def test_get__unknown() -> None:
    with raises(LookupError) as ex:
        Environment.get("foo")

    assert str(ex.value) == 'Environment "foo" not found'
