import os
import time

import pytest

from uncertainty_engine.client import Client


# NOTE: For these tests to run successfully, the following environment variables must be set:
# UE_USER_EMAIL: A user email that has been registered with the Uncertainty Engine service.
# UE_DEPLOYMENT_URL: The deployment URL for the Uncertainty Engine service.
@pytest.mark.parametrize(
    "test_user_email, deployment_url",
    [(os.environ["UE_USER_EMAIL"], os.environ["UE_DEPLOYMENT_URL"])],
    indirect=True,
)
class TestClientMethods:
    def test_list_nodes(self, client: Client):
        """
        Verify that the list_nodes method can be poked successfully.

        Args:
            client: A Client instance.
        """
        client.list_nodes()

    def test_queue_node(self, client: Client):
        """
        Verify that an add node can be queued successfully.

        Args:
            client: A Client instance.
        """
        node_name = "demo.Add"
        inputs = {
            "lhs": 1,
            "rhs": 2,
        }  # Inputs are left hand side and right hand side of equation

        job_id = client.queue_node(node=node_name, input=inputs)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestClientMethods.job_id = job_id

    def test_job_status(self, client: Client):
        """
        Verify that the job_status method can be poked successfully.

        Args:
            client: A Client instance.
        """
        job_id = TestClientMethods.job_id
        response = client.job_status(job_id)

        status = "STARTED"
        while status == "STARTED":
            response = client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert response["status"] == "SUCCESS"

    def test_view_token(self, client: Client):
        """
        Verify that the view_token method can be poked successfully.

        Args:
            client: A Client instance.
        """
        client.view_tokens()
