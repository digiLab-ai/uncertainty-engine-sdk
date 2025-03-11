import time

from uncertainty_engine.client import Client, ValidStatus
from uncertainty_engine.nodes.base import Node


class TestNodeAdd:
    def test_queue_node(self, e2e_client: Client):
        """
        Verify that the base Node object can be used to successfully queue a job.

        Args:
            e2e_client: A Client instance.
        """
        node_name = "Add"
        input = {
            "lhs": 1,
            "rhs": 2,
        }  # Inputs are left hand side and right hand side of equation

        job_id = e2e_client.queue_node(node=Node(node_name, **input))

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestNodeAdd.job_id = job_id

    def test_result(self, e2e_client: Client):
        """
        Verify that the job has been successfully executed.

        Args:
            e2e_client: A Client instance.
        """
        job_id = TestNodeAdd.job_id
        response = e2e_client.job_status(job_id)

        status = ValidStatus.PENDING.value
        while status not in [ValidStatus.SUCCESS.value, ValidStatus.FAILURE.value]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == ValidStatus.SUCCESS.value
        assert response["outputs"] == {"ans": 3}
