from uncertainty_engine.client import Client, DEFAULT_DEPLOYMENT


# __init__


def test_init_default(test_user_email: str):
    """
    Verify that the Client class can be instantiated with the default deployment.

    Args:
        test_user_email: An email address for testing.
    """
    client = Client(email=test_user_email)

    assert client.email == test_user_email
    assert client.deployment == DEFAULT_DEPLOYMENT


def test_init_custom(test_user_email: str):
    """
    Verify that the Client class can be instantiated with a custom deployment.

    Args:
        test_user_email: An email address for testing.
    """
    custom_deployment = "http://example.com"
    client = Client(email=test_user_email, deployment=custom_deployment)

    assert client.deployment == custom_deployment
