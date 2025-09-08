from typing import Any

from typeguard import typechecked

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import handle_input_deprecation


@typechecked
class Workflow(Node):
    """
    Execute a workflow of nodes.

    Args:
        graph: The graph of nodes to execute.
        requested_output: The requested output from the workflow.
        external_input_id: String identifier that refers to external inputs to the
            graph. Default is "_".
        inputs: The inputs to the workflow. Defaults to None.
        input: **DEPRECATED** The inputs to the workflow. Use `inputs` instead.
            Will be removed in a future version.

    Raises:
        ValueError: if both `inputs` and `input` are `None`, or if both are provided.

    Example:
        >>> workflow = Workflow(
        ...     graph=graph.nodes,
        ...     inputs=graph.external_input,
        ...     requested_output={
        ...         "Result": {"node_name": "Download", "node_handle": "file"}
        ...     }
        ... )
        >>> client.queue_node(workflow)
        "<job_id>"
    """

    node_name: str = "Workflow"

    def __init__(
        self,
        graph: dict[str, Any],
        requested_output: dict[str, Any],
        external_input_id: str = "_",
        inputs: dict[str, Any] | None = None,
        input: dict[str, Any] | None = None,
    ):
        # TODO: Remove once `input` is removed and make `inputs` required
        final_inputs = handle_input_deprecation(input, inputs)

        if final_inputs is None:
            raise ValueError("'inputs' must be provided.")

        # Store as Workflow attributes
        self.graph = graph
        self.requested_output = requested_output
        self.external_input_id = external_input_id
        self.inputs = final_inputs

        super().__init__(
            node_name=self.node_name,
            external_input_id=external_input_id,
            graph=graph,
            inputs=final_inputs,
            requested_output=requested_output,
        )
