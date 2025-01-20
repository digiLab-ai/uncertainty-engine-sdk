from unittest.mock import Mock, patch

import pytest

from uncertainty_engine.client import DEFAULT_DEPLOYMENT, Client


@pytest.fixture(scope="class")
def test_user_email():
    """
    An email address for testing.
    """
    return "a.user@digilab.co.uk"


@pytest.fixture(scope="class")
def client(test_user_email):
    """Fixture to initialize the Client class once per test class."""
    return Client(email=test_user_email)


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


class TestClientMethods:
    def test_list_nodes(self, client: Client):
        """
        Verify that the list_nodes method pokes the correct endpoint.

        Args:
            test_user_email: An email address for testing.
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = [{"node_a": "I'm a node."}]
            mock_get.return_value = mock_response

            response = client.list_nodes()

            assert response == [{"node_a": "I'm a node."}]
            mock_get.assert_called_once_with(f"{DEFAULT_DEPLOYMENT}/nodes/list")

    def test_queue_node(self, client: Client):
        """
        Verify that the queue_node method pokes the correct endpoint with the user defined input.

        Args:
            test_user_email: An email address for testing.
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.json.return_value = "job_id"
            mock_post.return_value = mock_response

            response = client.queue_node(node="node_a", input={"key": "value"})

            assert response == "job_id"
            mock_post.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/nodes/queue",
                json={
                    "email": client.email,
                    "node": "node_a",
                    "input": {"key": "value"},
                },
            )

    def test_job_status(self, client: Client):
        """
        Verify that the job_status method pokes the correct endpoint with the user defined job_id.

        Args:
            test_user_email: An email address for testing.
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"status": "running"}
            mock_get.return_value = mock_response

            response = client.job_status(job_id="job_id")

            assert response == {"status": "running"}
            mock_get.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/nodes/status/job_id"
            )

    def test_view_tokens(self, client: Client):
        """
        Verify that the view_tokens method pokes the correct endpoint.

        Args:
            test_user_email: An email address for testing.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = 10
            mock_get.return_value = mock_response

            response = client.view_tokens()

            assert response == 10
            mock_get.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/tokens/user/{client.email}"
            )
