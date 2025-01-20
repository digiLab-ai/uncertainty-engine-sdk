import pytest

from uncertainty_engine.client import Client, DEFAULT_DEPLOYMENT


@pytest.fixture(scope="class")
def test_user_email(request):
    """
    An email address for testing.
    """
    return getattr(request, "param", "a.user@digilab.co.uk")


@pytest.fixture(scope="class")
def deployment_url(request):
    """
    The deployment URL for the Uncertainty Engine service.
    """
    return getattr(request, "param", DEFAULT_DEPLOYMENT)


@pytest.fixture(scope="class")
def client(test_user_email: str, deployment_url: str):
    """Fixture to initialize the Client class once per test class."""
    return Client(email=test_user_email, deployment=deployment_url)
