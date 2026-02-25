import os
import time

import pytest
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

    @pytest.mark.skipif(
        os.getenv("UE_ENVIRONMENT") != "dev",
        reason="Get node versions feature only available in dev environment",
    )
    def test_get_node_versions(self, e2e_client: Client):
        """
        Verify that the node versions can be retrieved successfully.

        Args:
            e2e_client: A Client instance.
        """
        node_id = "Add"
        versions = e2e_client.get_node_versions(node_id)
        assert isinstance(versions, list)
        assert all(isinstance(v, (str, int)) for v in versions)
        assert len(versions) > 0

    @pytest.mark.skipif(
        os.getenv("UE_ENVIRONMENT") != "dev",
        reason="Query node versions feature only available in dev environment",
    )
    def test_query_nodes(self, e2e_client: Client):
        """
        Verify that query_nodes returns expected node info dict on success.

        Args:
            e2e_client: A Client instance.
        """
        nodes = [{"node_id": "Add", "version": "latest"}]
        result = e2e_client.query_nodes(nodes)
        assert "Add@latest" in result
        node_info = result["Add@latest"]
        assert node_info.id == "Add"
        assert node_info.label == "Add"
