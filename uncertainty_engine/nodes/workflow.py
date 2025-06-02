from typeguard import typechecked

from uncertainty_engine.nodes.base import Node


@typechecked
class Workflow(Node):
    """
    Execute a workflow of nodes.

    Args:
        graph: The graph of nodes to execute.
        input: The input to the workflow.
        requested_output: The requested output from the workflow.
        external_input_id: String identifier that refers to external inputs to the graph.
            Default is "_".

    Example:
        >>> workflow = Workflow(
        ...     graph=graph.nodes,
        ...     input=graph.external_input,
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
        graph: dict,
        input: dict,
        requested_output: dict,
        external_input_id: str = "_",
    ):
        super().__init__(
            node_name=self.node_name,
            external_input_id=external_input_id,
            graph=graph,
            inputs=input,
            requested_output=requested_output,
        )
