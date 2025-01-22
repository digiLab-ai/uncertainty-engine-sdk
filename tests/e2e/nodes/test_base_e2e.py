import os
import time

import pytest

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.base import Node


# NOTE: For these tests to run successfully, the following environment variables must be set:
# UE_USER_EMAIL: A user email that has been registered with the Uncertainty Engine service.
# UE_DEPLOYMENT_URL: The deployment URL for the Uncertainty Engine service.
@pytest.mark.parametrize(
    "test_user_email, deployment_url",
    [(os.environ["UE_USER_EMAIL"], os.environ["UE_DEPLOYMENT_URL"])],
    indirect=True,
)
class TestNodeAdd:
    def test_queue_node(self, client: Client):
        """
        Verify that the base Node object can be used to successfully queue a job.

        Args:
            client: A Client instance.
        """
        node_name = "demo.Add"
        input = {
            "lhs": 1,
            "rhs": 2,
        }  # Inputs are left hand side and right hand side of equation

        job_id = client.queue_node(node=Node(node_name, **input))

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestNodeAdd.job_id = job_id

    def test_result(self, client: Client):
        """
        Verify that the job has been successfully executed.

        Args:
            client: A Client instance.
        """
        job_id = TestNodeAdd.job_id
        response = client.job_status(job_id)

        status = "STARTED"
        while status == "STARTED":
            response = client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert response["output"] == {"ans": 3}
