import time

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
        respone = e2e_client.list_nodes(category="demo")

        # There should only be one node in the demo category
        assert len(respone) == 1
        assert respone[0]["category"] == "demo"
        assert respone[0]["type"] == "Add"

    def test_queue_node(self, e2e_client: Client):
        """
        Verify that an add node can be queued successfully.

        Args:
            e2e_client: A Client instance.
        """
        node_name = "demo.Add"
        inputs = {
            "lhs": 1,
            "rhs": 2,
        }  # Inputs are left hand side and right hand side of equation

        job_id = e2e_client.queue_node(node=node_name, input=inputs)

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

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert response["status"] == "SUCCESS"

    def test_view_token(self, e2e_client: Client):
        """
        Verify that the view_token method can be poked successfully.

        Args:
            e2e_client: A Client instance.
        """
        e2e_client.view_tokens()


def test_failure_bad_client(e2e_client: Client):
    """
    Verify an error is returned when an unknown client is used.
    """

    client = e2e_client
    client.email = "not_a_valid_email@mail.com"

    node_name = "demo.Add"
    inputs = {
        "lhs": 1,
        "rhs": 2,
    }  # Inputs are left hand side and right hand side of equation

    job_id = client.queue_node(node=node_name, input=inputs)

    status = "PENDING"
    while status not in ["SUCCESS", "FAILURE"]:
        response = e2e_client.job_status(job_id)
        status = response["status"]
        time.sleep(5)

    assert response["status"] == "FAILURE"
    assert "error" in response
