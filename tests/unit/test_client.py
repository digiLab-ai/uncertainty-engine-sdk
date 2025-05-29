from unittest.mock import patch

import pytest

from tests.mock_api_invoker import mock_core_api
from uncertainty_engine.client import DEFAULT_DEPLOYMENT, Client, Job, ValidStatus
from uncertainty_engine.nodes.base import Node

# __init__


def test_init_default() -> None:
    """
    Verify that the Client class can be instantiated with the default deployment.
    """

    client = Client()

    assert client.deployment == DEFAULT_DEPLOYMENT


def test_init_custom() -> None:
    """
    Verify that the Client class can be instantiated with a custom deployment.
    """
    custom_deployment = "http://example.com"
    client = Client(deployment=custom_deployment)

    assert client.deployment == custom_deployment


class TestClientMethods:
    def test_list_nodes(self, client: Client):
        """
        Verify that the list_nodes method pokes the correct endpoint.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_get(
                "/nodes/list",
                {"node_a": {"node_a": "I'm a node."}},
            )

            response = client.list_nodes()

            assert response == [{"node_a": "I'm a node."}]

    def test_list_nodes_category(self, client: Client):
        """
        Verify that the list_nodes method filters nodes by specified category.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_get(
                "/nodes/list",
                {
                    "node_a": {
                        "node_a": "I'm a node.",
                        "category": "cat_a",
                    },
                    "node_b": {
                        "node_b": "I'm another node.",
                        "category": "cat_b",
                    },
                },
            )

            response = client.list_nodes(category="cat_a")

            assert response == [{"node_a": "I'm a node.", "category": "cat_a"}]

    def test_queue_node_name_input(self, client: Client, mock_job: Job):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined by it's name and input.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/queue",
                expect_body={
                    "email": client.email,
                    "node_id": mock_job.node_id,
                    "inputs": {"key": "value"},
                },
                response=mock_job.job_id,
            )

            response = client.queue_node(
                node=mock_job.node_id,
                input={"key": "value"},
            )

        assert response == mock_job

    def test_job_status(self, client: Client, mock_job: Job):
        """
        Verify that the job_status method pokes the correct endpoint with the user defined job_id.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"status": "running"}

            response = client.job_status(mock_job)

            assert response == {"status": "running"}
            mock_get.assert_called_once_with(
                f"{DEFAULT_DEPLOYMENT}/nodes/status/{mock_job.node_id}/{mock_job.job_id}"
            )

    def test_queue_node_node_input(self, client: Client, mock_job: Job):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined as an object.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/queue",
                expect_body={
                    "email": client.email,
                    "node_id": mock_job.node_id,
                    "inputs": {"key": "value"},
                },
                response=mock_job.job_id,
            )

            node_name = mock_job.node_id
            inputs = {"key": "value"}
            node = Node(node_name, **inputs)
            response = client.queue_node(node)

            assert response == mock_job

    def test_queue_node_name_no_input(self, client: Client):
        """
        Verify that an error is raised if the user tries to queue a node defined by its name with no inputs.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_post("/nodes/queue", response="job_id")

            with pytest.raises(ValueError):
                client.queue_node(node="node_a")

    def test_wait_for_job(self, client: Client, mock_job: Job):
        """
        Verify that the _wait_for_job method pokes the correct endpoint and behaves as expected.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get, patch(
            "uncertainty_engine.client.STATUS_WAIT_TIME",
            0.1,  # Reduce wait time for testing
        ):
            # Use side_effect with a lambda to return different JSON values
            mock_get.return_value.json.side_effect = [
                {"status": ValidStatus.PENDING.value},
                {"status": ValidStatus.STARTED.value},
                {"status": ValidStatus.SUCCESS.value},
            ]

            response = client._wait_for_job(mock_job)

            assert response == {"status": ValidStatus.SUCCESS.value}
            assert mock_get.call_count == 3

            # Assert all calls are made to the same endpoint
            expected_url = f"{DEFAULT_DEPLOYMENT}/nodes/status/{mock_job.node_id}/{mock_job.job_id}"
            for call in mock_get.call_args_list:
                assert call.args[0] == expected_url

    def test_wait_for_job_invalid_status(self, client: Client, mock_job: Job):
        """
        Verify that the _wait_for_job raises an error if the status is invalid.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """
        with patch("uncertainty_engine.client.requests.get") as mock_get:
            mock_get.return_value.json.return_value = {"status": "INVALID"}

            with pytest.raises(ValueError):
                client._wait_for_job(mock_job)

    def test_run_node(self, client: Client, mock_job: Job):
        """
        Verify that the run_node method queues a node and waits for it to complete.

        Args:
            client: A Client instance.
            mock_job: A Job instance
        """
        with patch(
            "uncertainty_engine.client.Client.queue_node"
        ) as mock_queue_node, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_node.return_value = mock_job
            mock_wait_for_job.return_value = {"status": ValidStatus.SUCCESS.value}

            client.run_node(node="node_a", input={"key": "value"})

            mock_queue_node.assert_called_once_with("node_a", {"key": "value"})
            mock_wait_for_job.assert_called_once_with(mock_job)
