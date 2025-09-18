import time

from uncertainty_engine_types import JobStatus

from uncertainty_engine.client import Client


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

    def test_node_info(self, e2e_client: Client):
        """
        Verify that the node_info method returns correct information
        for the Add node.
        Args:
            e2e_client: A Client instance.
        """
        node_id = "Add"
        node_info = e2e_client.node_info(node_id)

        assert node_info.id == "Add"
        assert node_info.label == "Add"
        assert node_info.category == "Basic"
        assert node_info.description == "Add two numbers"
        assert node_info.long_description == "Add two numbers"
        assert node_info.image_name == "uncertainty-engine-add-node"
        assert node_info.cost == 1

        # Check inputs
        assert "lhs" in node_info.inputs
        assert node_info.inputs["lhs"].type == "float"
        assert node_info.inputs["lhs"].label == "LHS"
        assert node_info.inputs["lhs"].description == "Left-hand side of the addition"

        assert "rhs" in node_info.inputs
        assert node_info.inputs["rhs"].type == "float"
        assert node_info.inputs["rhs"].label == "RHS"
        assert node_info.inputs["rhs"].description == "Right-hand side of the addition"

        # Check outputs
        assert "ans" in node_info.outputs
        assert node_info.outputs["ans"].type == "float"
        assert node_info.outputs["ans"].label == "Answer"
        assert node_info.outputs["ans"].description == "Result of the addition"

        # Check requirements
        assert node_info.requirements.cpu == 256
        assert node_info.requirements.gpu is False
        assert node_info.requirements.memory == 512
        assert node_info.requirements.timeout == 15

        # Check URLs
        assert node_info.load_balancer_url.startswith("http://dev-un-uncer")
        assert node_info.queue_url.startswith("https://sqs.eu-west-2.amazonaws.com/")
