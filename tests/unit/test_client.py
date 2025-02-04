from unittest.mock import patch

import pytest

from uncertainty_engine.client import DEFAULT_DEPLOYMENT, Client
from uncertainty_engine.nodes.base import Node

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
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = [{"node_a": "I'm a node."}]

            response = client.list_nodes()

            assert response == [{"node_a": "I'm a node."}]
            mock_get.assert_called_once_with(f"{DEFAULT_DEPLOYMENT}/nodes/list")

    def test_list_nodes_category(self, client: Client):
        """
        Verify that the list_nodes method filters nodes by specified category.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = [
                {"node_a": "I'm a node.", "category": "cat_a"},
                {"node_b": "I'm another node.", "category": "cat_b"},
            ]

            response = client.list_nodes(category="cat_a")

            assert response == [{"node_a": "I'm a node.", "category": "cat_a"}]
            mock_get.assert_called_once_with(f"{DEFAULT_DEPLOYMENT}/nodes/list")

    def test_queue_node_name_input(self, client: Client):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined by it's name and input.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.post") as mock_post:
            mock_post.return_value.json.return_value = "job_id"

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
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"status": "running"}

            response = client.job_status(job_id="job_id")

            assert response == {"status": "running"}
            mock_get.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/nodes/status/job_id"
            )

    def test_view_tokens(self, client: Client):
        """
        Verify that the view_tokens method pokes the correct endpoint.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = 10

            response = client.view_tokens()

            assert response == 10
            mock_get.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/tokens/user/{client.email}"
            )

    def test_queue_node_node_input(self, client: Client):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined as an object.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.post") as mock_post:
            mock_post.return_value.json.return_value = "job_id"

            node_name = "node_a"
            inputs = {"key": "value"}
            node = Node(node_name, **inputs)
            response = client.queue_node(node)

            assert response == "job_id"
            mock_post.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/nodes/queue",
                json={
                    "email": client.email,
                    "node": "node_a",
                    "input": {"key": "value"},
                },
            )

    def test_queue_node_name_no_input(self, client: Client):
        """
        Verify that an error is raised if the user tries to queue a node defined by its name with no inputs.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.post") as mock_post:
            mock_post.return_value.json.return_value = "job_id"

            with pytest.raises(ValueError):
                client.queue_node(node="node_a")

    def test_wait_for_job(self, client: Client):
        """
        Verify that the _wait_for_job method pokes the correct endpoint and behaves as expected.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get, patch(
            "uncertainty_engine.client.STATUS_WAIT_TIME",
            0.1,  # Reduce wait time for testing
        ):
            # Use side_effect with a lambda to return different JSON values
            mock_get.return_value.json.side_effect = [
                {"status": "PENDING"},
                {"status": "STARTED"},
                {"status": "SUCCESS"},
            ]

            response = client._wait_for_job(job_id="job_id")

            assert response == {"status": "SUCCESS"}
            assert mock_get.call_count == 3

            # Assert all calls are made to the same endpoint
            expected_url = f"{DEFAULT_DEPLOYMENT}/nodes/status/job_id"
            for call in mock_get.call_args_list:
                assert call.args[0] == expected_url

    def test_wait_for_job_invalid_status(self, client: Client):
        """
        Verify that the _wait_for_job raises an error if the status is invalid.

        Args:
            client: A Client instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"status": "INVALID"}

            with pytest.raises(ValueError):
                client._wait_for_job(job_id="job_id")

    def test_run_node(self, client: Client):
        """
        Verify that the run_node method queues a node and waits for it to complete.

        Args:
            client: A Client instance.
        """
        with patch(
            "uncertainty_engine.client.Client.queue_node"
        ) as mock_queue_node, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_node.return_value = "job_id"
            mock_wait_for_job.return_value = {"status": "SUCCESS"}

            client.run_node(node="node_a", input={"key": "value"})

            mock_queue_node.assert_called_once_with("node_a", {"key": "value"})
            mock_wait_for_job.assert_called_once_with("job_id")
