import time

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.sensor_designer import (
    BuildSensorDesigner,
    ScoreSensorDesign,
    SuggestSensorDesign,
)


class TestFullSet:
    """
    Verify successful execution of the all the sensor designer nodes.
    """

    def test_queue_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
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

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestFullSet.job_id_build = job_id

    def test_result_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestFullSet.job_id_build
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response

        TestFullSet.sensor_designer = response["output"]["sensor_designer"]

    def test_queue_suggest(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        sensor_designer = TestFullSet.sensor_designer
        node = SuggestSensorDesign(
            sensor_designer=sensor_designer, num_sensors=1, num_eval=1
        )

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestFullSet.job_id_suggest = job_id

    def test_result_suggest(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestFullSet.job_id_suggest
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response

        TestFullSet.suggested_design = response["output"]["suggested_design"]

    def test_queue_score(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        sensor_designer = TestFullSet.sensor_designer
        suggested_design = TestFullSet.suggested_design
        node = ScoreSensorDesign(
            sensor_designer=sensor_designer, design=suggested_design
        )

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestFullSet.job_id_score = job_id

    def test_result_score(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestFullSet.job_id_score
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response


class TestBuildNoQoI:
    """
    Verify successful execution of the BuildSensorDesigner node when no QoI data is provided.
    """

    def test_queue_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        # Define the required data
        sensor_data = {
            "sensor_0_0": [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10],
            "sensor_0_1": [1.11, 1.12, 1.13, 1.14, 1.15, 1.16, 1.17, 1.18, 1.19, 11.10],
            "sensor_0_2": [2.21, 2.22, 2.23, 2.24, 2.25, 2.26, 2.27, 2.28, 2.29, 22.10],
        }
        sigma = 0.01

        node = BuildSensorDesigner(
            sensor_data=sensor_data,
            sigma=sigma,
        )

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestBuildNoQoI.job_id_build = job_id

    def test_result_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestBuildNoQoI.job_id_build
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response


class TestBuildNoSigma:
    """
    Verify successful execution of the BuildSensorDesigner node when no sigma is provided.
    """

    def test_queue_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
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

        node = BuildSensorDesigner(
            sensor_data=sensor_data,
            quantities_of_interest_data=qoi_data,
        )

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestBuildNoSigma.job_id_build = job_id

    def test_result_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestBuildNoSigma.job_id_build
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response


class TestBuildListSigma:
    """
    Verify successful execution of the BuildSensorDesigner node when a list of sigma values is provided.
    """

    def test_queue_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
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
        sigma = [0.01, 0.02, 0.03]

        node = BuildSensorDesigner(
            sensor_data=sensor_data,
            quantities_of_interest_data=qoi_data,
            sigma=sigma,
        )

        job_id = e2e_client.queue_node(node)

        # Add the job_id as an attribute of the test class so that it can be used in other tests
        TestBuildListSigma.job_id_build = job_id

    def test_result_build(self, e2e_client: Client):
        """
        Args:
            e2e_client: A Client instance.
        """
        job_id = TestBuildListSigma.job_id_build
        response = e2e_client.job_status(job_id)

        status = "PENDING"
        while status not in ["SUCCESS", "FAILURE"]:
            response = e2e_client.job_status(job_id)
            status = response["status"]
            time.sleep(5)

        assert status == "SUCCESS"
        assert "output" in response
