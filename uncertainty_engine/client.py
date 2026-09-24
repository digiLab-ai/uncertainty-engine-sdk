import warnings
from copy import deepcopy
from os import environ
from time import sleep
from typing import Any, Optional, Union

from pydantic import BaseModel, ValidationError
from requests import HTTPError
from typeguard import typechecked
from uncertainty_engine_types import (
    JobInfo,
    JobStatus,
    NodeInfo,
    NodeQuery,
    NodeQueryRequest,
    OverrideWorkflowInput,
    OverrideWorkflowOutput,
    RunWorkflowRequest,
)

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
from uncertainty_engine.dynamic_nodes import DynamicNodes
from uncertainty_engine.environments import Environment
from uncertainty_engine.exceptions import IncompleteCredentials
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import handle_input_deprecation

STATUS_WAIT_TIME = 5  # An interval of 5 seconds to wait between status checks while waiting for a job to complete

# Stands in for the version in a cache key when the Node Registry chose
# the version, rather than the caller naming one. It is not a valid
# version, so it cannot collide with a real one.
DEFAULT_VERSION_KEY = "__default__"


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
            >>> client = Client()
            >>> client.authenticate()
            >>> add_node = Node(node_name="Add", lhs=1, rhs=2, label="add")
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

        self._node_info_cache: dict[str, NodeInfo] = {}
        """
        Node schemas resolved so far, keyed by `<node>@<version>`. A
        node's default version is additionally stored under
        `<node>@{DEFAULT_VERSION_KEY}`, so that a default lookup and a
        lookup of the version it resolved to share one entry.
        """

        self._node_list_cache: list[dict[str, Any]] | None = None
        """
        The node catalogue, as returned by `/nodes/list`, or `None`
        while it has not been loaded.
        """

        self._nodes = DynamicNodes(self)

    def _cache_node_info(self, node_info: NodeInfo, is_default: bool) -> None:
        """
        Store a resolved node schema in the cache.

        Args:
            node_info: The schema to store.
            is_default: Whether this is the node's default version, in
                which case it is stored under the default key as well.
        """

        self._node_info_cache[f"{node_info.id}@{node_info.version_node}"] = node_info

        if is_default:
            self._node_info_cache[f"{node_info.id}@{DEFAULT_VERSION_KEY}"] = node_info

    def clear_node_cache(self) -> None:
        """
        Forget every cached node schema and the node catalogue.

        Node information is cached for the life of the client and never
        expires on its own, so this is how to pick up a node that has
        been deployed, or a new version of one, without building a new
        client.

        Example:
            >>> client.clear_node_cache()
        """

        self._node_info_cache.clear()
        self._node_list_cache = None

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
        account_id: str | None = None,
    ) -> None:
        """
        Authenticate the user with the Uncertainty Engine.

        Args:
            account_id : **DEPRECATED** This parameter is no longer used
                and will be removed in the next release. Defaults to
                `None`. The account ID is now obtained from HTTP
                headers.
        """
        self.auth_service.authenticate(account_id)

        # Propagate new authentication state to all providers
        self._update_all_providers()

    @property
    def nodes(self) -> DynamicNodes:
        """
        Build any node by name, resolving its schema from the Node
        Registry on demand.

        Node schemas are fetched one node at a time, as they are needed;
        the catalogue is never loaded up front.

        Example:
            >>> add = client.nodes.Add(lhs=1, rhs=2, label="add")
            >>> add = client.nodes("Add", lhs=1, rhs=2, label="add")
            >>> client.nodes.available()
            >>> client.nodes.describe("Add").inputs
            >>> pinned = client.nodes.with_versions({"Add": "0.2.0"})
        """

        return self._nodes

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

        Note:
            The catalogue is fetched once and cached for the life of the
            client, so a node deployed afterwards will not appear until
            `clear_node_cache()` is called. Every node it returns also
            seeds the node schema cache, so building any listed node
            afterwards makes no further request.

        Example:
            >>> all_nodes = client.list_nodes()
            >>> print(all_nodes)
        """

        if self._node_list_cache is None:
            nodes = self.core_api.get("/nodes/list")
            self._node_list_cache = [node_info for node_info in nodes.values()]

            for node_info in self._node_list_cache:
                try:
                    # `/nodes/list` returns one entry per node, at the
                    # version the registry considers default, so each
                    # seeds both of that node's cache keys.
                    self._cache_node_info(NodeInfo(**node_info), is_default=True)
                except ValidationError:
                    # A malformed entry must not stop the catalogue from
                    # being listed; it simply does not seed the cache.
                    continue

        # A deep copy, so that a caller mutating what they get back -
        # the list or the dicts in it - cannot corrupt the cache. The
        # cost is trivial next to the request this replaces.
        node_list = deepcopy(self._node_list_cache)

        if category is not None:
            node_list = [node for node in node_list if node["category"] == category]

        return node_list

    def get_default_node_info(self, node: str) -> NodeInfo:
        """
        Obtain a `NodeInfo` object for a node's default version.

        The Node Registry decides which version is the default: it
        prefers "latest", and otherwise takes the highest available
        version. Nodes that are versioned with an integer only are
        resolved the same way. The SDK never works the version out
        itself, which is why `get_node_info` keeps its `version`
        argument required: "latest" cannot be selected by accidentally
        omitting an argument.

        Args:
            node: The ID of the node to get information about.

        Returns:
            Information about the node's default version as a `NodeInfo`
            object.

        Raises:
            HTTPError: If the node does not exist (404) or another HTTP
                error occurs.

        Note:
            The resolved default is cached for the life of the client,
            so a version deployed afterwards is not picked up until
            `clear_node_cache()` is called.

        Example:
            >>> node_info = client.get_default_node_info("Add")
            >>> print(node_info.version_node)
            >>> print(node_info.inputs)
        """

        key = f"{node}@{DEFAULT_VERSION_KEY}"

        if key in self._node_info_cache:
            return self._node_info_cache[key]

        node_info = NodeInfo(**self.core_api.get(f"/nodes/{node}"))
        self._cache_node_info(node_info, is_default=True)

        return node_info

    def get_node_info(
        self,
        node: str,
        version: str | int,
    ) -> NodeInfo:
        """
        Obtain a `NodeInfo` object containing metadata, input/output
        schema, and configuration details for a given node and version.

        The `version` is required. Use `get_default_node_info` to let
        the Node Registry pick the default version instead.

        Args:
            node: The ID of the node to get information about.
            version: The version of the node to get information about.

        Returns:
            Information about the node as a `NodeInfo` object.

        Raises:
            KeyError: If the node information is not found in the
                response.

        Note:
            The schema is cached for the life of the client, keyed by
            the version as requested, so a moving alias such as
            "latest" keeps returning the schema it first resolved to
            until `clear_node_cache()` is called.

        Example:
            >>> node_info = client.get_node_info("Add", "0.2.0")
            >>> print(node_info.inputs)
            >>> print(node_info.outputs)
        """

        key = f"{node}@{version}"

        if key in self._node_info_cache:
            return self._node_info_cache[key]

        query = NodeQuery(node_id=node, version=version)
        response = self.query_nodes([query])
        versioned_key = str(query)

        try:
            node_info = response[versioned_key]

            self._cache_node_info(node_info, is_default=False)

            # The requested version is not always the one it resolves to
            # (e.g. "latest"), so key the request as well, or asking for
            # it again would miss the cache.
            self._node_info_cache[key] = node_info

            return node_info
        except KeyError:
            raise KeyError(
                f"Node '{node}' with version '{version}' was not found. "
                "Please check the node name and version, or use "
                "`list_nodes()` and `get_node_versions()` to see "
                "available options."
            )

    def get_node_versions(self, node_id: str) -> list[str | int]:
        """
        Get node versions for a specific node.

        Args:
            node_id: The ID of the node to get versions for.

        Returns:
            A list of available versions for the node.

        Raises:
            HTTPError: If the node does not exist (404) or another HTTP error occurs.

        Example:
            >>> versions = client.get_node_versions("Add")
            >>> print(versions)
        """
        try:
            versions = self.core_api.get(f"/nodes/{node_id}/versions")
            return versions
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                reason = e.response.reason
                raise HTTPError(
                    f"404 {reason}: The node '{node_id}' does not exist.",
                    response=e.response,
                ) from e
            raise

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
                "node_id": node,
                "inputs": final_inputs,
            },
        )

        return Job(node_id=node, job_id=job_id)

    def queue_workflow(
        self,
        project_id: str,
        workflow_id: str,
        inputs: Optional[
            Union[list[OverrideWorkflowInput], list[dict[str, Any]]]
        ] = None,
        outputs: Optional[
            Union[list[OverrideWorkflowOutput], list[dict[str, Any]]]
        ] = None,
    ) -> Job:
        """
        Queue a workflow for execution

        Args:
            project_id: The ID of the project where the workflow is saved
            workflow_id: The ID of the workflow you want to run
            inputs: Optional list of inputs to override within the workflow
            outputs: Optional list of outputs to override. If passed previous outputs are overridden

        Returns:
            A Job object representing the queued job.

        Example:
            >>> # Basic workflow execution
            >>> job = client.queue_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id"
            ... )

            >>> # With input overrides
            >>> override_inputs = [
            ...     OverrideWorkflowInput(
            ...         node_label="input_node_label",
            ...         input_handle="input_parameter_name",
            ...         value="new_value"
            ...     )
            ... ]
            >>> job = client.queue_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id",
            ...     inputs=override_inputs
            ... )

            >>> # With output overrides
            >>> override_outputs = [
            ...     OverrideWorkflowOutput(
            ...         node_label="output_node_label",
            ...         output_handle="output_parameter_name",
            ...         output_label="custom_output_name"
            ...     )
            ... ]
            >>> job = client.queue_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id",
            ...     outputs=override_outputs
            ... )
        """
        if inputs is not None and len(inputs) > 0:
            has_dicts = False
            converted_inputs: list[OverrideWorkflowInput] = []
            for item in inputs:
                if isinstance(item, dict):
                    has_dicts = True
                    converted_inputs.append(OverrideWorkflowInput(**item))
                else:
                    converted_inputs.append(item)

            if has_dicts:
                warnings.warn(
                    "Passing dict objects for 'inputs' is deprecated. "
                    "Please use OverrideWorkflowInput objects instead. "
                    "This functionality will be removed in a future version.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                inputs = converted_inputs

        if outputs is not None and len(outputs) > 0:
            has_dicts = False
            converted_outputs: list[OverrideWorkflowOutput] = []
            for item in outputs:
                if isinstance(item, dict):
                    has_dicts = True
                    converted_outputs.append(OverrideWorkflowOutput(**item))
                else:
                    converted_outputs.append(item)

            if has_dicts:
                warnings.warn(
                    "Passing dict objects for 'outputs' is deprecated. "
                    "Please use OverrideWorkflowOutput objects instead. "
                    "This functionality will be removed in a future version.",
                    DeprecationWarning,
                    stacklevel=2,
                )
                outputs = converted_outputs

        payload = RunWorkflowRequest(inputs=inputs, outputs=outputs)

        job_id = self.core_api.post(
            f"/workflows/projects/{project_id}/workflows/{workflow_id}/run",
            payload.model_dump(),
        )
        return Job(node_id="Workflow", job_id=job_id)

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

    def run_workflow(
        self,
        project_id: str,
        workflow_id: str,
        inputs: Optional[
            Union[list[OverrideWorkflowInput], list[dict[str, Any]]]
        ] = None,
        outputs: Optional[
            Union[list[OverrideWorkflowOutput], list[dict[str, Any]]]
        ] = None,
    ) -> JobInfo:
        """
        Run a workflow synchronously.

        Args:
            project_id: The ID of the project where the workflow is saved
            workflow_id: The ID of the workflow you want to run
            inputs: Optional list of inputs to override within the workflow
            outputs: Optional list of outputs to override. If passed previous outputs are overridden

        Returns:
            A JobInfo object containing the response data of the job.

        Example:
            >>> # Basic workflow execution
            >>> job_info = client.run_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id"
            ... )

            >>> # With input overrides
            >>> override_inputs = [
            ...     OverrideWorkflowInput(
            ...         node_label="input_node_label",
            ...         input_handle="input_parameter_name",
            ...         value="new_value"
            ...     )
            ... ]
            >>> job_info = client.run_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id",
            ...     inputs=override_inputs
            ... )

            >>> # With output overrides
            >>> override_outputs = [
            ...     OverrideWorkflowOutput(
            ...         node_label="output_node_label",
            ...         output_handle="output_parameter_name",
            ...         output_label="custom_output_name"
            ...     )
            ... ]
            >>> job_info = client.run_workflow(
            ...     project_id="your_project_id",
            ...     workflow_id="your_workflow_id",
            ...     outputs=override_outputs
            ... )
        """
        # catch deprecation warning from `queue_workflow`
        with warnings.catch_warnings():
            warnings.simplefilter("always")
            job = self.queue_workflow(project_id, workflow_id, inputs, outputs)

        return self._wait_for_job(job)

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

    def cancel_job(self, job: Job) -> bool:
        """
        Cancel a job.

        Args:
            job: The job to cancel.

        Returns:
            True if the job was successfully cancelled.

        Example:
            >>> job = client.queue_node(add_node)
            >>> client.cancel_job(job)
            True
        """
        response = self.core_api.post(f"/nodes/jobs/{job.job_id}/cancel", {})
        return response

    def view_tokens(self) -> int:
        """
        View the number of tokens currently available to the user's
        organisation.

        Returns:
            The number of tokens currently available to the user's
            organisation.

        Example:
            >>> tokens = client.view_tokens()
            >>> print(f"Available tokens: {tokens}")
        """

        tokens = self.core_api.get("/organizations/tokens/available")

        return tokens

    def query_nodes(self, queries: list[NodeQuery]) -> dict[str, NodeInfo]:
        """
        Query information for a set of nodes specified by node_id and version.

        Args:
            queries: A list of NodeQuery objects.

        Returns:
            Dictionary mapping '<node_id>@<version>' to NodeInfo objects.

        Raises:
            HTTPError: If any node is not found or another HTTP error occurs.
                If multiple errors, detail will contain all errors.

        Example:
            >>> from uncertainty_engine_types import NodeQuery
            >>> queries = [
            ...     NodeQuery(node_id="nodeA", version="1"),
            ...     NodeQuery(node_id="nodeB", version="2")
            ... ]
            >>> result = client.query_nodes(queries)
            >>> print(result)
            >>> print(result["nodeA@1"])
        """
        request_body = NodeQueryRequest(nodes=queries).model_dump()
        try:
            response = self.core_api.post("/nodes/query", request_body)
            return {k: NodeInfo(**v) for k, v in response.items()}
        except HTTPError as e:
            if e.response is None:
                raise

            try:
                errors = e.response.json().get("detail", {}).get("errors")
            except (ValueError, TypeError, AttributeError):
                errors = None

            if errors:
                raise HTTPError(
                    f"Node query errors: {errors}",
                    response=e.response,
                ) from e
            raise

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
