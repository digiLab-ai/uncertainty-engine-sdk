import time

from uncertainty_engine.client import Client, ValidStatus
from uncertainty_engine.nodes.basic import Add


class TestAdd:
    def test_queue_node(self, e2e_client: Client):
        """
        Verify that the base Node object can be used to successfully queue a job.

        Args:
            e2e_client: A Client instance.
        """
        add = Add(lhs=1, rhs=2)

        job_id = e2e_client.queue_node(node=add)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestAdd.job_id = job_id

    def test_result(self, e2e_client: Client):
        """
        Verify that the job has been successfully executed.

        Args:
            e2e_client: A Client instance.
        """
        job_id = TestAdd.job_id
        response = e2e_client.job_status(job_id)

        status = ValidStatus.PENDING.value
        while status not in [ValidStatus.SUCCESS.value, ValidStatus.FAILURE.value]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == ValidStatus.SUCCESS.value
        assert response["outputs"] == {"ans": 3}
