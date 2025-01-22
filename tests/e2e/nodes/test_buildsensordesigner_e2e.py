import os
import time

import pytest

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.sensor_designer import BuildSensorDesigner


# NOTE: For these tests to run successfully, the following environment variables must be set:
# UE_USER_EMAIL: A user email that has been registered with the Uncertainty Engine service.
# UE_DEPLOYMENT_URL: The deployment URL for the Uncertainty Engine service.
@pytest.mark.parametrize(
    "test_user_email, deployment_url",
    [(os.environ["UE_USER_EMAIL"], os.environ["UE_DEPLOYMENT_URL"])],
    indirect=True,
)
class TestAllParams:
    """
    Verify successful execution of the BuildSensorDesigner node with all parameters.
    """

    def test_queue_node(self, client: Client):
        """
        Args:
            client: A Client instance.
        """
        # Define the required data
        sensor_data = {
            "sensor_0_0": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10],
            "sensor_0_1": [1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 11.10],
            "sensor_0_2": [2.21, 2.22, 2.23, 2.24, 2.25, 2.26, 2.27, 2.28, 2.29, 22.10],
        }
        qoi_data = {
            "qoi_1": [1.23, 1.32, 2.31, 2.13, 3.21, 3.12, 1.11, 2.22, 3.33, 32.23],
            "qoi_2": [1.11, 2.22, 3.33, 4.44, 5.55, 6.66, 7.77, 8.88, 9.99, 1010.10],
        }
        sigma = 0.01

        node = BuildSensorDesigner(
            sensor_data=sensor_data,
            quantities_of_interest_data=qoi_data,
            sigma=sigma,
        )

        job_id = client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestAllParams.job_id = job_id

    def test_result(self, client: Client):
        """
        Args:
            client: A Client instance.
        """
        job_id = TestAllParams.job_id
        response = client.job_status(job_id)

        status = "STARTED"
        while status not in ["SUCCESS", "FAILURE"]:
            response = client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response
