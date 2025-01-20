import pytest


@pytest.fixture(scope="class")
def test_user_email():
    """
    An email address for testing.
    There is an account record associated with this email address in the database.
    """
    return "test@digilab.co.uk"
