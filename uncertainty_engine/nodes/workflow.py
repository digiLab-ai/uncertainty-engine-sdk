import warnings
from typing import Any

from typeguard import typechecked

from uncertainty_engine.nodes.base import Node


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
        # TODO: Make this required once `input` parameter is removed
        inputs: dict[str, Any] | None = None,
        # Deprecated: Use `inputs` instead. Will be removed in next release
        input: dict[str, Any] | None = None,
    ):
        if input is not None and inputs is not None:
            raise ValueError(
                "Cannot specify both 'input' and 'inputs'. Use 'inputs' only."
            )

        if input is not None:
            warnings.warn(
                "The 'input' parameter is deprecated and will be removed in the next "
                "release. Use 'inputs' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            final_inputs = input
        elif inputs is not None:
            final_inputs = inputs
        else:
            raise ValueError("'inputs' must be provided.")

        super().__init__(
            node_name=self.node_name,
            external_input_id=external_input_id,
            graph=graph,
            inputs=final_inputs,
            requested_output=requested_output,
        )
