import time

from uncertainty_engine_types import JobStatus

from uncertainty_engine.client import Client
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.nodes.basic import Add
from uncertainty_engine.nodes.workflow import Workflow


class TestClientMethods:
    def test_list_nodes(self, e2e_client: Client):
        """
        Verify that the list_nodes method can be poked successfully.

        Args:
            e2e_client: A Client instance.
        """
        e2e_client.list_nodes()

    def test_list_nodes_category(self, e2e_client: Client):
        """
        Verify that nodes can be filtered by category.

        Args:
            e2e_client: A Client instance.
        """
        respone = e2e_client.list_nodes(category="Basic")

        # There should only be one node in the demo category
        assert len(respone) == 1
        assert respone[0]["category"] == "Basic"
        assert respone[0]["id"] == "Add"

    def test_queue_node(self, e2e_client: Client):
        """
        Verify that an add node can be queued successfully.

        Args:
            e2e_client: A Client instance.
        """
        node_name = "Add"
        inputs = {
            "lhs": 1,
            "rhs": 2,
        }  # Inputs are left hand side and right hand side of equation

        job_id = e2e_client.queue_node(node=node_name, inputs=inputs)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestClientMethods.job_id = job_id

    def test_job_status(self, e2e_client: Client):
        """
        Verify that the job_status method can be poked successfully.

        Args:
            e2e_client: A Client instance.
        """
        job_id = TestClientMethods.job_id
        response = e2e_client.job_status(job_id)

        status = JobStatus.PENDING.value
        while status not in [JobStatus.COMPLETED.value, JobStatus.FAILED.value]:
            response = e2e_client.job_status(job_id)
            status = response.status.value
            time.sleep(5)

        assert status == JobStatus.COMPLETED.value

    def test_view_tokens(self, e2e_client: Client) -> None:
        """
        Verify that the `view_tokens` method returns an integer
        representing the number of available tokens.

        Args:
            e2e_client: A Client instance.
        """
        tokens = e2e_client.view_tokens()
        assert isinstance(tokens, int)
        assert tokens >= 0

    def test_get_node_info(self, e2e_client: Client) -> None:
        """
        Test that the `Add` node info returns the correct id, and that
        all inputs and outputs exist and are not empty.

        Args:
            e2e_client: A Client instance.
        """

        node_info = e2e_client.get_node_info("Add")
        assert node_info.id == "Add"
        assert node_info.inputs
        assert node_info.outputs

    def test_queue_workflow_basic(
        self, e2e_client: Client, test_project_id: str, test_workflow_id: str
    ) -> None:
        job_id = e2e_client.queue_workflow(
            project_id=test_project_id,
            workflow_id=test_workflow_id,
        )

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value
