from os import environ
from time import sleep
from typing import Any, Optional, Union

from pydantic import BaseModel
from typeguard import typechecked
from uncertainty_engine_types import JobInfo, JobStatus

from uncertainty_engine.api_invoker import ApiInvoker, HttpApiInvoker
from uncertainty_engine.api_providers import (
    ApiProviderBase,
    AuthProvider,
    ProjectsProvider,
    ResourceProvider,
    WorkflowsProvider,
)
from uncertainty_engine.auth_service import AuthService
from uncertainty_engine.cognito_authenticator import CognitoAuthenticator
from uncertainty_engine.environments import Environment
from uncertainty_engine.exceptions import IncompleteCredentials
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import handle_input_deprecation

STATUS_WAIT_TIME = 5  # An interval of 5 seconds to wait between status checks while waiting for a job to complete


# TODO: Move this to the uncertainty_engine_types package.
class Job(BaseModel):
    """
    Represents a job in the Uncertainty Engine.
    """

    node_id: str
    job_id: str


@typechecked
class Client:
    def __init__(
        self,
        env: Environment | str = "prod",
    ):
        """
        A client for interacting with the Uncertainty Engine.

        Args:
            env: Environment configuration or name of a deployed environment.
                Defaults to the main Uncertainty Engine environment.

        Example:
            >>> client = Client(
            ...     env=Environment(
            ...         cognito_user_pool_client_id="<COGNITO USER POOL APPLICATION CLIENT ID>",
            ...         core_api="<UNCERTAINTY ENGINE CORE API URL>",
            ...         region="<REGION>",
            ...         resource_api="<UNCERTAINTY ENGINE RESOURCE SERVICE API URL>",
            ...     ),
            ... )
            >>> client.authenticate("<ACCOUNT ID>")
            >>> add_node = Add(lhs=1, rhs=2, label="add")
            >>> client.queue_node(add_node)
            "<job-id>"
        """

        self.env = Environment.get(env) if isinstance(env, str) else env
        """
        Uncertainty Engine environment.
        """

        authenticator = CognitoAuthenticator(
            self.env.region,
            self.env.cognito_user_pool_client_id,
        )

        self.auth_service = AuthService(
            authenticator,
            self._get_resource_token,
        )

        self.core_api: ApiInvoker = HttpApiInvoker(
            self.auth_service,
            self.env.core_api,
        )
        """
        Core API interaction.
        """

        self.auth = AuthProvider(
            self.auth_service,
            self.env.resource_api,
        )
        """
        Resource Service Authorisation API client.
        """

        self.projects = ProjectsProvider(
            self.auth_service,
            self.env.resource_api,
        )
        self.resources = ResourceProvider(
            self.auth_service,
            self.env.resource_api,
        )
        self.workflows = WorkflowsProvider(
            self.auth_service,
            self.env.resource_api,
        )

        self._providers: list[ApiProviderBase] = [
            self.auth,
            self.projects,
            self.resources,
            self.workflows,
        ]

    def _get_resource_token(self) -> str:
        """Get a Resource Service API token."""
        self.auth.update_api_authentication()
        return self.auth.get_tokens().access_token

    def _update_all_providers(self) -> None:
        """Update authentication for all API providers."""
        for provider in self._providers:
            provider.update_api_authentication()

    def authenticate(
        self,
        account_id: str,
    ) -> None:
        """
        Authenticate the user with the Uncertainty Engine"

        Args:
            account_id : The account ID to authenticate with.
        """
        self.auth_service.authenticate(account_id)

        # Propagate new authentication state to all providers
        self._update_all_providers()

    @property
    def email(self) -> str:
        """
        The user's username, which is expected to be their email address.

        Raises:
            IncompleteCredentials: Raised if the UE_USERNAME environment
                variable is not set.
        """

        env_var = "UE_USERNAME"

        if username := environ.get(env_var):
            return username

        raise IncompleteCredentials(env_var)

    def list_nodes(self, category: Optional[str] = None) -> list:
        """
        List all available nodes in the specified deployment.

        Args:
            category: The category of nodes to list. If not specified, all nodes are listed.
                Defaults to ``None``.

        Returns:
            List of available nodes. Each list item is a dictionary of information about the node.
        """

        nodes = self.core_api.get("/nodes/list")
        node_list = [node_info for node_info in nodes.values()]

        if category is not None:
            node_list = [node for node in node_list if node["category"] == category]

        return node_list

    def queue_node(
        self,
        node: Union[str, Node],
        inputs: Optional[dict[str, Any]] = None,
        input: Optional[dict[str, Any]] = None,
    ) -> Job:
        """
        Queue a node for execution.

        Args:
            node: The name of the node to execute or the node object itself.
            inputs: The input data for the node. If the node is defined by its name,
                this is required. Defaults to ``None``.
            input: **DEPRECATED** The input data for the node. Use `inputs` instead.
                Will be removed in a future version.

        Returns:
            A Job object representing the queued job.
        """
        # TODO: Remove once `input` is removed and make `inputs` required
        final_inputs = handle_input_deprecation(input, inputs)

        if isinstance(node, Node):
            node, final_inputs = node()
        elif isinstance(node, str) and final_inputs is None:
            raise ValueError(
                "Input data/parameters are required when specifying a node by name."
            )

        job_id = self.core_api.post(
            "/nodes/queue",
            {
                "email": self.email,
                "node_id": node,
                "inputs": final_inputs,
            },
        )

        return Job(node_id=node, job_id=job_id)

    def run_node(
        self,
        node: Union[str, Node],
        inputs: Optional[dict[str, Any]] = None,
        input: Optional[dict[str, Any]] = None,
    ) -> JobInfo:
        """
        Run a node synchronously.

        Args:
            node: The name of the node to execute or the node object itself.
            inputs: The input data for the node. If the node is defined by its name,
                this is required. Defaults to ``None``.
            input: **DEPRECATED** The input data for the node. Use `inputs` instead.
                Will be removed in a future version.

        Returns:
            A JobInfo object containing the response data of the job.
        """
        # TODO: Remove once `input` is removed and make `inputs` required
        final_inputs = handle_input_deprecation(input, inputs)

        job_id = self.queue_node(node, final_inputs)
        return self._wait_for_job(job_id)

    def job_status(self, job: Job) -> JobInfo:
        """
        Check the status of a job.

        Args:
            job: The job to check.

        Returns:
            A JobInfo object containing the response data of the job.
            Example:
                JobInfo(
                status=<JobStatus.COMPLETED: 'completed'>,
                message='Job completed at 2025-07-23 09:10:59.146669',
                inputs={'lhs': 1, 'rhs': 2},
                outputs={'ans': 3.0}
                )
        """
        response_data = self.core_api.get(f"/nodes/status/{job.node_id}/{job.job_id}")
        return JobInfo(**response_data)

    def view_tokens(self) -> Optional[int]:
        """
        View how many tokens the user currently has available.

        Returns:
            Number of tokens the user currently has available.
        """

        # The token service for the new backend is not yet implemented.
        # This is a placeholder for when the service is implemented.
        # TODO: Make a request to the token service to get the user's token balance once it is implemented.
        # response = requests.get(f"{self.deployment}/tokens/user/{self.email}")
        tokens = 100

        return tokens

    def _wait_for_job(self, job: Job) -> JobInfo:
        """
        Wait for a job to complete.

        Args:
            job: The job to wait for.

        Returns:
            A JobInfo object containing the response data of the job.
        """
        response = self.job_status(job)
        status = JobStatus(response.status.value)
        while not status.is_terminal():
            sleep(STATUS_WAIT_TIME)
            response = self.job_status(job)
            status = JobStatus(response.status.value)

        return response
