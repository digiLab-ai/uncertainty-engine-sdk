import pytest

from uncertainty_engine.auth_provider import AuthProvider


@pytest.fixture
def auth_provider() -> AuthProvider:
    """Fixture for an AuthProvider instance."""
    return AuthProvider()


def test_init(auth_provider: AuthProvider):
    """
    Test that a new AuthProvider has no account_id set.

    Args:
        auth_provider: An instance of AuthProvider.
    """
    assert auth_provider.account_id is None
    assert auth_provider.is_authenticated is False


def test_authenticate(auth_provider: AuthProvider):
    """
    Test that calling authenticate sets the account_id.

    Args:
        auth_provider: An instance of AuthProvider.
    """
    # Setup
    test_account_id = "test-account-123"

    # Call the method
    auth_provider.authenticate(test_account_id)

    # Verify result
    assert auth_provider.account_id == test_account_id
    assert auth_provider.is_authenticated is True


def test_authenticate_multiple_calls(auth_provider: AuthProvider):
    """
    Test that authenticate can be called multiple times, updating the account_id.

    Args:
        auth_provider: An instance of AuthProvider.
    """
    # Setup
    first_account_id = "first-account"
    second_account_id = "second-account"

    # Call authenticate with first ID
    auth_provider.authenticate(first_account_id)
    assert auth_provider.account_id == first_account_id
    assert auth_provider.is_authenticated is True

    # Call authenticate with second ID
    auth_provider.authenticate(second_account_id)
    assert auth_provider.account_id == second_account_id
    assert auth_provider.is_authenticated is True


def test_is_authenticated_property_when_not_authenticated(auth_provider: AuthProvider):
    """
    Test is_authenticated property returns False when account_id is None.

    Args:
        auth_provider: An instance of AuthProvider.
    """
    # Verify initial state
    assert auth_provider.account_id is None
    assert auth_provider.is_authenticated is False


def test_is_authenticated_property_when_authenticated(auth_provider: AuthProvider):
    """
    Test is_authenticated property returns True when account_id is set.

    Args:
        auth_provider: An instance of AuthProvider.
    """
    # Setup
    auth_provider.account_id = "test-account"

    # Verify result
    assert auth_provider.is_authenticated is True
