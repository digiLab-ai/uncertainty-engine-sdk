from unittest.mock import patch, Mock
from requests import HTTPError

import pytest
from uncertainty_engine_types import (
    JobInfo,
    JobStatus,
    OverrideWorkflowInput,
    OverrideWorkflowOutput,
)

from tests.mock_api_invoker import mock_core_api
from uncertainty_engine import Client, Environment
from uncertainty_engine.client import Job
from uncertainty_engine.nodes.base import Node


def test_init_default() -> None:
    """
    Verify that the Client class can be instantiated with the default deployment.
    """

    client = Client()
    assert client.env == Environment.get("prod")


def test_init_with_named_env() -> None:
    client = Client(env="dev")
    assert client.env == Environment.get("dev")


def test_init_with_custom_env() -> None:
    """
    Verify that the Client class can be instantiated with a custom deployment.
    """

    custom_env = Environment(
        cognito_user_pool_client_id="custom_cognito_user_pool_client_id",
        core_api="custom_core_api",
        # `region` must be a real region so the Client can instantiate a Cognito
        # authenticator.
        region="eu-west-2",
        resource_api="custom_resource_api",
    )

    client = Client(env=custom_env)
    assert client.env == custom_env


class TestClientMethods:
    def test_list_nodes(self, client: Client):
        """
        Verify that the list_nodes method pokes the correct endpoint.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_get(
                "/nodes/list",
                {"node_a": {"node_a": "I'm a node."}},
            )

            response = client.list_nodes()

            assert response == [{"node_a": "I'm a node."}]

    def test_list_nodes_category(self, client: Client):
        """
        Verify that the list_nodes method filters nodes by specified category.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_get(
                "/nodes/list",
                {
                    "node_a": {
                        "node_a": "I'm a node.",
                        "category": "cat_a",
                    },
                    "node_b": {
                        "node_b": "I'm another node.",
                        "category": "cat_b",
                    },
                },
            )

            response = client.list_nodes(category="cat_a")

            assert response == [{"node_a": "I'm a node.", "category": "cat_a"}]

    def test_queue_node_name_input(self, client: Client, mock_job: Job):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined by it's name and input.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/queue",
                expect_body={
                    "node_id": mock_job.node_id,
                    "inputs": {"key": "value"},
                },
                response=mock_job.job_id,
            )

            response = client.queue_node(
                node=mock_job.node_id,
                inputs={"key": "value"},
            )

        assert response == mock_job

    def test_job_status(self, client: Client, mock_job: Job):
        """
        Verify that the job_status method pokes the correct endpoint with the user-defined job_id.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        mock_job_info = JobInfo(
            status=JobStatus.RUNNING,
            message="Job is running",
            inputs={"lhs": 1, "rhs": 2},
            outputs=None,
        )

        with mock_core_api(client) as api:
            api.expect_get(
                f"/nodes/status/{mock_job.node_id}/{mock_job.job_id}",
                mock_job_info.model_dump(),
            )

            response = client.job_status(mock_job)

            assert isinstance(response, JobInfo)
            assert response == mock_job_info

    def test_cancel_job(self, client: Client, mock_job: Job):
        """
        Verify that the cancel_job method pokes the correct endpoint with the user-defined job_id.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_post(
                f"/nodes/jobs/{mock_job.job_id}/cancel",
                expect_body={},
                response=True,
            )

            response = client.cancel_job(mock_job)

            assert response is True

    def test_queue_node_node_input(self, client: Client, mock_job: Job):
        """
        Verify that the queue_node method pokes the correct endpoint with the user
        defined input when the node is defined as an object.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/queue",
                expect_body={
                    "node_id": mock_job.node_id,
                    "inputs": {"key": "value"},
                },
                response=mock_job.job_id,
            )

            node_name = mock_job.node_id
            inputs = {"key": "value"}
            node = Node(node_name, **inputs)
            response = client.queue_node(node)

            assert response == mock_job

    def test_queue_node_name_no_input(self, client: Client):
        """
        Verify that an error is raised if the user tries to queue a node defined by its name with no inputs.

        Args:
            client: A Client instance.
        """

        with mock_core_api(client) as api:
            api.expect_post("/nodes/queue", response="job_id")

            with pytest.raises(ValueError):
                client.queue_node(node="node_a")

    def test_wait_for_job(self, client: Client, mock_job: Job):
        """
        Verify that the _wait_for_job method pokes the correct endpoint and behaves as expected.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api, patch(
            "uncertainty_engine.client.STATUS_WAIT_TIME",
            0.1,  # Reduce wait time for testing
        ):

            pending = JobInfo(
                status=JobStatus.PENDING,
                message="Job is pending",
                inputs={},
                outputs=None,
            )
            running = JobInfo(
                status=JobStatus.RUNNING,
                message="Job is running",
                inputs={},
                outputs=None,
            )
            completed = JobInfo(
                status=JobStatus.COMPLETED,
                message="Job completed",
                inputs={},
                outputs={"result": 42},
            )

            api.expect_get(
                f"/nodes/status/{mock_job.node_id}/{mock_job.job_id}",
                pending.model_dump(),
                running.model_dump(),
                completed.model_dump(),
            )

            response = client._wait_for_job(mock_job)

            assert isinstance(response, JobInfo)
            assert response.status == JobStatus.COMPLETED
            assert response.outputs == {"result": 42}

    def test_wait_for_job_invalid_status(self, client: Client, mock_job: Job):
        """
        Verify that the _wait_for_job raises an error if the status is invalid.

        Args:
            client: A Client instance.
            mock_job: A Job instance.
        """

        with mock_core_api(client) as api:
            api.expect_get(
                f"/nodes/status/{mock_job.node_id}/{mock_job.job_id}",
                {"status": "INVALID"},
            )

            with pytest.raises(ValueError):
                client._wait_for_job(mock_job)

    def test_run_node(self, client: Client, mock_job: Job):
        """
        Verify that the run_node method queues a node and waits for it to complete.

        Args:
            client: A Client instance.
            mock_job: A Job instance
        """
        with patch(
            "uncertainty_engine.client.Client.queue_node"
        ) as mock_queue_node, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_node.return_value = mock_job
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Job completed",
                inputs={"key": "value"},
                outputs={"result": 42},
            )

            client.run_node(node="node_a", inputs={"key": "value"})

            mock_queue_node.assert_called_once_with("node_a", {"key": "value"})
            mock_wait_for_job.assert_called_once_with(mock_job)

    def test_view_tokens(self, client: Client) -> None:
        """
        Verify that the `view_tokens` method pokes the correct endpoint.

        Args:
            client: A Client instance.
        """
        with mock_core_api(client) as api:
            api.expect_get(
                "/organizations/tokens/available",
                123,
            )

            client.view_tokens()

    def test_get_node_info(self, client: Client):
        """
        Verify that the `get_node_info` method pokes the correct
        endpoint and returns a `NodeInfo` object.

        Args:
            client: A `Client` instance.
        """
        with mock_core_api(client) as api:
            node_id = "node_a"
            node_info_dict = {
                "id": node_id,
                "label": node_id,
                "category": "test_category",
                "description": "A test node",
                "long_description": "A long description for the test node.",
                "image_name": "test_image.png",
                "cost": 10,
                "inputs": {},
                "outputs": {},
                "version_types_lib": "1.0.0",
                "version_base_image": 1,
                "version_node": 1,
            }
            api.expect_get(f"/nodes/{node_id}", node_info_dict)

            client.get_node_info(node_id)

    def test_queue_workflow_basic(self, client: Client):
        """
        Verify that the queue_workflow method pokes the correct endpoint with basic parameters.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": None,
                    "outputs": None,
                },
                response=expected_job_id,
            )

            response = client.queue_workflow(
                project_id=project_id,
                workflow_id=workflow_id,
            )

            expected_job = Job(node_id="Workflow", job_id=expected_job_id)
            assert response == expected_job

    def test_queue_workflow_with_inputs(self, client: Client):
        """
        Verify that the queue_workflow method handles input overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_inputs = [
            OverrideWorkflowInput(
                node_label="input_node_label",
                input_handle="input_parameter_name",
                value="new_value",
            )
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": [override_inputs[0].model_dump()],
                    "outputs": None,
                },
                response=expected_job_id,
            )

            response = client.queue_workflow(
                project_id=project_id,
                workflow_id=workflow_id,
                inputs=override_inputs,
            )

            expected_job = Job(node_id="Workflow", job_id=expected_job_id)
            assert response == expected_job

    def test_queue_workflow_with_outputs(self, client: Client):
        """
        Verify that the queue_workflow method handles output overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_outputs = [
            OverrideWorkflowOutput(
                node_label="output_node_label",
                output_handle="output_parameter_name",
                output_label="custom_output_name",
            )
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": None,
                    "outputs": [override_outputs[0].model_dump()],
                },
                response=expected_job_id,
            )

            response = client.queue_workflow(
                project_id=project_id,
                workflow_id=workflow_id,
                outputs=override_outputs,
            )

            expected_job = Job(node_id="Workflow", job_id=expected_job_id)
            assert response == expected_job

    def test_queue_workflow_with_inputs_and_outputs(self, client: Client):
        """
        Verify that the queue_workflow method handles both input and output overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_inputs = [
            OverrideWorkflowInput(
                node_label="input_node_label",
                input_handle="input_parameter_name",
                value="new_value",
            )
        ]
        override_outputs = [
            OverrideWorkflowOutput(
                node_label="output_node_label",
                output_handle="output_parameter_name",
                output_label="custom_output_name",
            )
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": [override_inputs[0].model_dump()],
                    "outputs": [override_outputs[0].model_dump()],
                },
                response=expected_job_id,
            )

            response = client.queue_workflow(
                project_id=project_id,
                workflow_id=workflow_id,
                inputs=override_inputs,
                outputs=override_outputs,
            )

            expected_job = Job(node_id="Workflow", job_id=expected_job_id)
            assert response == expected_job

    def test_run_workflow(self, client: Client):
        """
        Verify that the run_workflow method queues a workflow and waits for it to complete.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        mock_job = Job(node_id="Workflow", job_id="test_job_id")

        with patch(
            "uncertainty_engine.client.Client.queue_workflow"
        ) as mock_queue_workflow, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_workflow.return_value = mock_job
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={},
                outputs={"result": 42},
            )

            result = client.run_workflow(project_id=project_id, workflow_id=workflow_id)

            mock_queue_workflow.assert_called_once_with(
                project_id, workflow_id, None, None
            )
            mock_wait_for_job.assert_called_once_with(mock_job)
            assert result.status == JobStatus.COMPLETED
            assert result.outputs == {"result": 42}

    def test_run_workflow_with_inputs(self, client: Client):
        """
        Verify that the run_workflow method handles input overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        override_inputs = [
            OverrideWorkflowInput(
                node_label="input_node_label",
                input_handle="input_parameter_name",
                value="new_value",
            )
        ]
        mock_job = Job(node_id="Workflow", job_id="test_job_id")

        with patch(
            "uncertainty_engine.client.Client.queue_workflow"
        ) as mock_queue_workflow, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_workflow.return_value = mock_job
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={"input_parameter_name": "new_value"},
                outputs={"result": "success"},
            )

            result = client.run_workflow(
                project_id=project_id, workflow_id=workflow_id, inputs=override_inputs
            )

            mock_queue_workflow.assert_called_once_with(
                project_id, workflow_id, override_inputs, None
            )
            mock_wait_for_job.assert_called_once_with(mock_job)
            assert result.status == JobStatus.COMPLETED

    def test_run_workflow_with_outputs(self, client: Client):
        """
        Verify that the run_workflow method handles output overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        override_outputs = [
            OverrideWorkflowOutput(
                node_label="output_node_label",
                output_handle="output_parameter_name",
                output_label="custom_output_name",
            )
        ]
        mock_job = Job(node_id="Workflow", job_id="test_job_id")

        with patch(
            "uncertainty_engine.client.Client.queue_workflow"
        ) as mock_queue_workflow, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_workflow.return_value = mock_job
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={},
                outputs={"custom_output_name": "success"},
            )

            result = client.run_workflow(
                project_id=project_id, workflow_id=workflow_id, outputs=override_outputs
            )

            mock_queue_workflow.assert_called_once_with(
                project_id, workflow_id, None, override_outputs
            )
            mock_wait_for_job.assert_called_once_with(mock_job)
            assert result.status == JobStatus.COMPLETED

    def test_run_workflow_with_inputs_and_outputs(self, client: Client):
        """
        Verify that the run_workflow method handles both input and output overrides correctly.

        Args:
            client: A Client instance.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        override_inputs = [
            OverrideWorkflowInput(
                node_label="input_node_label",
                input_handle="input_parameter_name",
                value="new_value",
            )
        ]
        override_outputs = [
            OverrideWorkflowOutput(
                node_label="output_node_label",
                output_handle="output_parameter_name",
                output_label="custom_output_name",
            )
        ]
        mock_job = Job(node_id="Workflow", job_id="test_job_id")

        with patch(
            "uncertainty_engine.client.Client.queue_workflow"
        ) as mock_queue_workflow, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            mock_queue_workflow.return_value = mock_job
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={"input_parameter_name": "new_value"},
                outputs={"custom_output_name": "success"},
            )

            result = client.run_workflow(
                project_id=project_id,
                workflow_id=workflow_id,
                inputs=override_inputs,
                outputs=override_outputs,
            )

            mock_queue_workflow.assert_called_once_with(
                project_id, workflow_id, override_inputs, override_outputs
            )
            mock_wait_for_job.assert_called_once_with(mock_job)
            assert result.status == JobStatus.COMPLETED

    def test_queue_workflow_with_dict_inputs_deprecation(self, client: Client):
        """
        Verify that the queue_workflow method raises a deprecation warning
        when dict inputs are used.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_inputs = [
            {
                "node_label": "input_node_label",
                "input_handle": "input_parameter_name",
                "value": "new_value",
            }
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": override_inputs,
                    "outputs": None,
                },
                response=expected_job_id,
            )

            with pytest.warns(
                DeprecationWarning,
                match="Passing dict objects for 'inputs' is deprecated",
            ):
                client.queue_workflow(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    inputs=override_inputs,
                )

    def test_queue_workflow_with_dict_outputs_deprecation(self, client: Client):
        """
        Verify that the queue_workflow method raises a deprecation warning
        when dict outputs are used.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_outputs = [
            {
                "node_label": "output_node_label",
                "output_handle": "output_parameter_name",
                "output_label": "custom_output_name",
            }
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": None,
                    "outputs": override_outputs,
                },
                response=expected_job_id,
            )

            with pytest.warns(
                DeprecationWarning,
                match="Passing dict objects for 'outputs' is deprecated",
            ):
                client.queue_workflow(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    outputs=override_outputs,
                )

    def test_run_workflow_with_dict_inputs_deprecation(self, client: Client):
        """
        Verify that the run_workflow method raises a deprecation warning
        when dict inputs are used.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_inputs = [
            {
                "node_label": "input_node_label",
                "input_handle": "input_parameter_name",
                "value": "new_value",
            }
        ]

        with mock_core_api(client) as api, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": override_inputs,
                    "outputs": None,
                },
                response=expected_job_id,
            )
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={"input_parameter_name": "new_value"},
                outputs={"result": "success"},
            )

            with pytest.warns(
                DeprecationWarning,
                match="Passing dict objects for 'inputs' is deprecated",
            ):
                client.run_workflow(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    inputs=override_inputs,
                )

    def test_run_workflow_with_dict_outputs_deprecation(self, client: Client):
        """
        Verify that the run_workflow method raises a deprecation warning
        when dict outputs are used.
        """
        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_outputs = [
            {
                "node_label": "output_node_label",
                "output_handle": "output_parameter_name",
                "output_label": "custom_output_name",
            }
        ]

        with mock_core_api(client) as api, patch(
            "uncertainty_engine.client.Client._wait_for_job"
        ) as mock_wait_for_job:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                expect_body={
                    "inputs": None,
                    "outputs": override_outputs,
                },
                response=expected_job_id,
            )
            mock_wait_for_job.return_value = JobInfo(
                status=JobStatus.COMPLETED,
                message="Workflow completed",
                inputs={},
                outputs={"custom_output_name": "success"},
            )

            with pytest.warns(
                DeprecationWarning,
                match="Passing dict objects for 'outputs' is deprecated",
            ):
                client.run_workflow(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    outputs=override_outputs,
                )

    def test_queue_workflow_deprecation_warning_on_any_item_in_inputs(
        self, client: Client
    ):
        """
        Test if any item in inputs is dict then throws deprecation warning
        """

        project_id = "test_project_id"
        workflow_id = "test_workflow_id"
        expected_job_id = "test_job_id"
        override_inputs = [
            OverrideWorkflowInput(
                node_label="input_node_label",
                input_handle="input_parameter_name",
                value="new_value",
            ),
            {
                "node_label": "input_node_label",
                "input_handle": "input_parameter_name",
                "value": "new_value",
            },
        ]

        with mock_core_api(client) as api:
            api.expect_post(
                f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
                response=expected_job_id,
            )

            with pytest.warns(
                DeprecationWarning,
                match="Passing dict objects for 'inputs' is deprecated",
            ):
                client.queue_workflow(
                    project_id=project_id,
                    workflow_id=workflow_id,
                    inputs=override_inputs,
                )

    def test_get_node_versions_happy_path(self, client: Client):
        """
        Verify that get_node_versions returns the expected versions list on success.
        """
        with mock_core_api(client) as api:
            node_id = "Add"
            expected_versions = ["0.2.0", "latest"]
            api.expect_get(f"/nodes/{node_id}/versions", expected_versions)
            result = client.get_node_versions(node_id)
            assert result == expected_versions

    def test_get_node_versions_404(self, client: Client):
        """
        Verify that get_node_versions raises HTTPError with 404 message if node not found.
        """
        with mock_core_api(client) as api:
            node_id = "MissingNode"
            response_404 = Mock()
            response_404.status_code = 404
            response_404.reason = "Not Found"
            http_error = HTTPError(response=response_404)
            api.expect_get(f"/nodes/{node_id}/versions", http_error)
            with pytest.raises(HTTPError) as exc_info:
                client.get_node_versions(node_id)
            assert exc_info.value.response.status_code == 404
            assert exc_info.value.response.reason == "Not Found"

    def test_get_node_versions_http_error_non_404(self, client: Client):
        """
        Verify that get_node_versions raises HTTPError for non-404 HTTP errors.
        """
        with mock_core_api(client) as api:
            node_id = "Add"
            response_500 = Mock()
            response_500.status_code = 500
            response_500.reason = "Internal Server Error"
            http_error = HTTPError(response=response_500)
            api.expect_get(f"/nodes/{node_id}/versions", http_error)
            with pytest.raises(HTTPError) as exc_info:
                client.get_node_versions(node_id)
            assert exc_info.value.response.status_code == 500
            assert exc_info.value.response.reason == "Internal Server Error"

    def test_get_node_versions_other_exception(self, client: Client):
        """
        Verify that get_node_versions raises any other exception as-is.
        """
        with mock_core_api(client) as api:
            node_id = "Add"
            api.expect_get(f"/nodes/{node_id}/versions", RuntimeError("boom"))
            with pytest.raises(RuntimeError, match="boom"):
                client.get_node_versions(node_id)
