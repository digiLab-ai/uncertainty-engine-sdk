import pytest

from uncertainty_engine.auth_service import AuthService


@pytest.fixture
def auth_service():
    """Fixture for an AuthService instance."""
    return AuthService()


def test_init(auth_service):
    """Test that a new AuthService has no account_id set."""
    assert auth_service.account_id is None
    assert auth_service.is_authenticated is False


def test_authenticate(auth_service):
    """Test that calling authenticate sets the account_id."""
    # Setup
    test_account_id = "test-account-123"

    # Call the method
    auth_service.authenticate(test_account_id)

    # Verify result
    assert auth_service.account_id == test_account_id
    assert auth_service.is_authenticated is True


def test_authenticate_multiple_calls(auth_service):
    """Test that authenticate can be called multiple times, updating the account_id."""
    # Setup
    first_account_id = "first-account"
    second_account_id = "second-account"

    # Call authenticate with first ID
    auth_service.authenticate(first_account_id)
    assert auth_service.account_id == first_account_id
    assert auth_service.is_authenticated is True

    # Call authenticate with second ID
    auth_service.authenticate(second_account_id)
    assert auth_service.account_id == second_account_id
    assert auth_service.is_authenticated is True


def test_is_authenticated_property_when_not_authenticated(auth_service):
    """Test is_authenticated property returns False when account_id is None."""
    # Verify initial state
    assert auth_service.account_id is None
    assert auth_service.is_authenticated is False


def test_is_authenticated_property_when_authenticated(auth_service):
    """Test is_authenticated property returns True when account_id is set."""
    # Setup
    auth_service.account_id = "test-account"

    # Verify result
    assert auth_service.is_authenticated is True
