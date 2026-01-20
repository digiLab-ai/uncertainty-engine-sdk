import time

import boto3

from uncertainty_engine_types import (
    JobStatus,
    OverrideWorkflowInput,
    OverrideWorkflowOutput,
)

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
        self,
        e2e_client: Client,
        project_id: str,
        workflow_id: str,
    ) -> None:
        """
        Test that a basic workflow can be queued and completed successfully,
        and that the output is as expected.

        """

        job_id = e2e_client.queue_workflow(
            project_id=project_id,
            workflow_id=workflow_id,
        )

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        assert response.outputs["outputs"]["add result"] == 9.0

    def test_queue_workflow_with_inputs(
        self,
        e2e_client: Client,
        project_id: str,
        workflow_id: str,
    ) -> None:
        """
        Verify that a workflow can be queued with overridden inputs and
        produces the expected output.

        """

        override_inputs = [
            OverrideWorkflowInput(
                node_label="num node",
                input_handle="value",
                value="12",
            ),
            OverrideWorkflowInput(
                node_label="add node",
                input_handle="lhs",
                value="12",
            ),
        ]

        job_id = e2e_client.queue_workflow(
            project_id=project_id,
            workflow_id=workflow_id,
            inputs=override_inputs,
        )

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        assert response.outputs["outputs"]["add result"] == 24.0

    def test_queue_workflow_with_outputs(
        self,
        e2e_client: Client,
        project_id: str,
        workflow_id: str,
    ) -> None:
        """
        Verify that workflows can be queued with overridden outputs.

        """

        override_outputs = [
            OverrideWorkflowOutput(
                node_label="num node",
                output_handle="value",
                output_label="number node output",
            )
        ]

        job_id = e2e_client.queue_workflow(
            project_id=project_id,
            workflow_id=workflow_id,
            outputs=override_outputs,
        )

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        assert response.outputs["outputs"]["number node output"] == 5.0

    def test_queue_workflow_with_inputs_and_outputs(
        self,
        e2e_client: Client,
        project_id: str,
        workflow_id: str,
    ) -> None:
        """
        Verify that a workflow can be queued with both input
        and output overrides.

        """

        override_inputs = [
            OverrideWorkflowInput(
                node_label="num node",
                input_handle="value",
                value="6",
            ),
            OverrideWorkflowInput(
                node_label="add node",
                input_handle="lhs",
                value="6",
            ),
        ]

        override_outputs = [
            OverrideWorkflowOutput(
                node_label="add node",
                output_handle="ans",
                output_label="add output override",
            )
        ]

        job_id = e2e_client.queue_workflow(
            project_id=project_id,
            workflow_id=workflow_id,
            inputs=override_inputs,
            outputs=override_outputs,
        )

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        assert response.outputs["outputs"]["add output override"] == 12.0

    def test_cancel_job(self, e2e_client: Client):
        """
        Verify that a job can be cancelled successfully.

        Args:
            e2e_client: A Client instance.
        """
        # Queue a job that we'll cancel
        node_name = "Add"
        inputs = {
            "lhs": 10,
            "rhs": 20,
        }

        job = e2e_client.queue_node(node=node_name, inputs=inputs)

        result = e2e_client.cancel_job(job)

        # Verify the cancellation was successful
        assert result is True

        # Verify the job status is cancelled
        job_info = e2e_client.job_status(job)
        assert job_info.status == JobStatus.CANCELLED

    def test_filter_dataset(self, e2e_client: Client):
        """
        Verify that the filter_dataset node filters data correctly.

        Args:
            e2e_client: A Client instance.
        """
        node_name = "FilterDataset"
        # Create a dataset with 10 rows and 4 columns
        csv_data = "col1,col2,col3,col4\n"
        for i in range(10):
            csv_data += f"{i * 4 + 1},{i * 4 + 2},{i * 4 + 3},{i * 4 + 4}\n"

        inputs = {
            "dataset": {"csv": csv_data},
            "columns": ["col1", "col2"],  # List of columns to keep
        }

        job_id = e2e_client.queue_node(node=node_name, inputs=inputs)

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        output_dataset = response.outputs["dataset"]
        assert output_dataset is not None
        assert isinstance(output_dataset, dict)
        assert "bucket" in output_dataset and "key" in output_dataset

        # Download from S3
        s3_client = boto3.client("s3", region_name=e2e_client.env.region)
        s3_object = s3_client.get_object(
            Bucket=output_dataset["bucket"], Key=output_dataset["key"]
        )
        output_csv = s3_object["Body"].read().decode("utf-8")

        # Verify the output dataset has all 10 rows
        output_lines = output_csv.strip().split("\n")
        # 1 header line + 10 data rows = 11 total lines
        assert len(output_lines) == 11, f"Expected 11 lines, got {len(output_lines)}"

        # Verify only col1 and col2 are present in the output
        header = output_lines[0]
        assert "col1" in header and "col2" in header
        assert "col3" not in header and "col4" not in header

    def test_filter_dataset_with_thinning(self, e2e_client: Client):
        """
        Verify that the filter_dataset node can thin data correctly,
        as part of filtering.

        Args:
            e2e_client: A Client instance.
        """
        node_name = "FilterDataset"
        # Create a dataset with 20 rows and 3 columns
        csv_data = "col1,col2,col3\n"
        for i in range(20):
            csv_data += f"{i * 3 + 1},{i * 3 + 2},{i * 3 + 3}\n"

        inputs = {
            "dataset": {"csv": csv_data},
            "columns": ["col1", "col2"],  # List of columns to keep
            "sample_fraction": 0.5,  # Thin to 50% of rows
        }

        job_id = e2e_client.queue_node(node=node_name, inputs=inputs)

        response = e2e_client._wait_for_job(job_id)

        status = response.status.value

        assert status == JobStatus.COMPLETED.value

        output_dataset = response.outputs["dataset"]
        assert output_dataset is not None
        assert isinstance(output_dataset, dict)
        assert "bucket" in output_dataset and "key" in output_dataset

        # TODO Code below here is pending
        # https://github.com/digiLab-ai/uncertainty-engine-filter-dataset-node/pull/22

        # Download from S3
        # s3_client = boto3.client("s3", region_name=e2e_client.env.region)
        # s3_object = s3_client.get_object(
        #     Bucket=output_dataset["bucket"], Key=output_dataset["key"]
        # )

        # output_csv = s3_object["Body"].read().decode("utf-8")

        # Verify the output dataset has been reduced by 50%
        # output_lines = output_csv.strip().split("\n")
        # assert len(output_lines) == 11, f"Expected 11 lines (50% reduction), got {len(output_lines)}"
