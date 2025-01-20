from unittest.mock import Mock, patch

from uncertainty_engine.client import DEFAULT_DEPLOYMENT, Client

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


# list_nodes


def test_list_nodes(test_user_email: str):
    """
    Verify that the list_nodes method pokes the correct endpoint.

    Args:
        test_user_email: An email address for testing.
    """
    client = Client(email=test_user_email)

    with patch("uncertainty_engine.client.requests.get") as mock_get:
        mock_response = Mock()
        mock_response.json.return_value = [{"node_a": "I'm a node."}]
        mock_get.return_value = mock_response

        response = client.list_nodes()

        assert response == [{"node_a": "I'm a node."}]
        mock_get.assert_called_once_with(f"{DEFAULT_DEPLOYMENT}/nodes/list")
