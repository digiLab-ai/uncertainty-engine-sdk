import time

from uncertainty_engine_types import Handle

from uncertainty_engine.client import Client, ValidStatus
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.basic import Add
from uncertainty_engine.nodes.workflow import Workflow


class TestWorkflow:
    """
    Verify successful execution of a simple addition workflow.
    """

    def test_queue_workflow(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        # Define an addition node
        add1 = Add(lhs=1, rhs=2)

        # Define the graph
        graph = Graph()

        # Add the addition node to the graph
        graph.add_node(add1, "add1")

        # Add another addition node to the graph
        graph.add_node(Add, "add2")

        # Define one of the inputs to the second addition node
        graph.add_input("add2_rhs", 2)
        graph.add_edge("_", "add2_rhs", "add2", "rhs")

        # Connect the first addition node to the second addition node
        graph.add_edge("add1", "ans", "add2", "lhs")

        # Define the workflow node
        workflow = Workflow(
            graph=graph.nodes,
            input=graph.external_input,
            requested_output={
                "a": Handle("_.add2_rhs").model_dump(),
                "b": Handle("add2.ans").model_dump(),
            },
        )

        # Queue the workflow
        job_id = e2e_client.queue_node(workflow)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestWorkflow.job_id = job_id

    def test_result_workflow(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestWorkflow.job_id
        response = e2e_client.job_status(job_id)

        status = ValidStatus.PENDING.value
        while status not in [ValidStatus.SUCCESS.value, ValidStatus.FAILURE.value]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == ValidStatus.SUCCESS.value
        assert "outputs" in response
        assert response["outputs"]["a"] == 2
        assert response["outputs"]["b"] == 5
