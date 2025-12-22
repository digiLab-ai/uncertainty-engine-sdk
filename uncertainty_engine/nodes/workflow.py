from typing import Any
from warnings import warn

from typeguard import typechecked
from uncertainty_engine_types import NodeInfo, ToolMetadata

from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.protocols import Client
from uncertainty_engine.utils import handle_input_deprecation
from uncertainty_engine.workflow_validator import WorkflowValidator


@typechecked
class Workflow(Node):
    """
    Execute a workflow of nodes.

    Args:
        graph: The graph of nodes to execute.
        inputs: The inputs to the workflow. Defaults to None.
        requested_output: The requested output from the workflow.
        external_input_id: String identifier that refers to external inputs to the
            graph. Default is "_".
        input: **DEPRECATED** The inputs to the workflow. Use `inputs` instead.
            Will be removed in a future version.
        tool_metadata: An optional `ToolMetadata` object containing the
            node input and output handles to be used as tools.
        client: An optional instance of the client being used. This is
            required for performing validation.

    Raises:
        ValueError: if both `inputs` and `input` are `None`, or if both are provided.

    Example:
        >>> client = Client()
        >>> workflow = Workflow(
        ...     graph=graph.nodes,
        ...     inputs=graph.external_input,
        ...     requested_output={
        ...         "Result": {"node_name": "Download", "node_handle": "file"}
        ...     },
        ...     client=client,
        ... )
        >>> client.queue_node(workflow)
        "<job_id>"
    """

    node_name: str = "Workflow"

    def __init__(
        self,
        graph: dict[str, Any],
        inputs: dict[str, Any] | None = None,
        requested_output: dict[str, Any] | None = None,
        external_input_id: str = "_",
        input: dict[str, Any] | None = None,
        tool_metadata: ToolMetadata | None = None,
        client: Client | None = None,
    ):
        # TODO: Remove once `input` is removed and make `inputs` required
        final_inputs = handle_input_deprecation(input, inputs)

        if final_inputs is None:
            raise ValueError("'inputs' must be provided.")

        if tool_metadata:
            tool_metadata.validate_complete()

            tool_metadata = tool_metadata if not tool_metadata.is_empty() else None

        # Store as Workflow attributes
        self.graph = graph
        self.requested_output = requested_output
        self.external_input_id = external_input_id
        self.inputs = final_inputs
        self.nodes_list = self._get_nodes_list(client) if client else None

        super().__init__(
            node_name=self.node_name,
            client=client,
            external_input_id=external_input_id,
            graph=graph,
            inputs=final_inputs,
            requested_output=requested_output,
            tool_metadata=tool_metadata,
        )

    @classmethod
    def from_graph(
        cls,
        graph_obj: Graph,
        requested_output: dict[str, Any] | None = None,
    ):
        """
        Create a Workflow from a graph object, automatically setting parameters.

        Args:
            graph_obj: The graph object with required attributes.
            requested_output: Optional requested output dict.

        Returns:
            Workflow instance
        """
        # Validate tool metadata completeness before creating workflow
        graph_obj.validate_tool_metadata()

        tool_metadata = (
            graph_obj.tool_metadata if not graph_obj.tool_metadata.is_empty() else None
        )

        return cls(
            graph=graph_obj.nodes,
            inputs=graph_obj.external_input,
            external_input_id=getattr(graph_obj, "external_input_id", "_"),
            tool_metadata=tool_metadata,
            requested_output=requested_output,
        )

    def _get_nodes_list(self, client: Client) -> list[NodeInfo] | None:
        """
        Returns a list of NodeInfo objects from the client, or None if
        the client is not provided or a validation error occurs.

        Args:
            client: Client to be used to fetch node information.
        """
        try:
            return [NodeInfo(**node_info) for node_info in client.list_nodes()]
        except Exception:
            warn(
                "Unable to get node info list. Workflow node will not be able to perform validation."
            )
            return None

    def validate(self) -> None:
        """
        Validates the entire workflow using the list of nodes fetched
        from the client and set as `self.nodes_list`:

        The error messages are collected and then re-raised once the
        all checks have finished.

        Raises:
            `ValueError`: If `self.nodes_list` is `None`.
            `WorkflowValidationError`: If validation fails. The error
                message will contain reasons for failure.
        """
        if self.nodes_list is None:
            raise ValueError("Nodes list is not available for validation.")

        validator = WorkflowValidator(
            node_info_list=self.nodes_list,
            graph=self.graph,
            inputs=self.inputs,
            requested_output=self.requested_output,
        )
        validator.validate()
