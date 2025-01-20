import pytest

from uncertainty_engine.client import Client


@pytest.fixture(scope="class")
def test_user_email(request):
    """
    An email address for testing.
    """
    return getattr(request, "param", "a.user@digilab.co.uk")


@pytest.fixture(scope="class")
def client(test_user_email):
    """Fixture to initialize the Client class once per test class."""
    return Client(email=test_user_email)
