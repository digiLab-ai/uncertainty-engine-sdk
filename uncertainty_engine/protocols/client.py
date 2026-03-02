from typing import Any, Protocol, runtime_checkable

from uncertainty_engine_types import NodeInfo


@runtime_checkable
class Client(Protocol):
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

    def get_node_info(self, node: str, version: str | int) -> NodeInfo:
        """
        Obtain a `NodeInfo` object containing metadata, input/output
        schema, and configuration details for a given node and version.

        Args:
            node: The ID of the node to get information about.
            version: The version of the node to get information about.
        """
        ...

    def list_nodes(self, category: str | None = None) -> list[dict[str, Any]]:
        """
        List all available nodes in the specified deployment.

        Args:
            category: The category of nodes to list. If not specified, all nodes are listed.
                Defaults to ``None``.

        Returns:
            List of available nodes. Each list item is a dictionary of information about the node.
        """
        ...
