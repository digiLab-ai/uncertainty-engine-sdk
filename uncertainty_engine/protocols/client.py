from typing import Protocol

from uncertainty_engine_types import NodeInfo


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

    def get_node_info(self, node_name: str) -> NodeInfo:
        """
        Get information about a specific node.

        Args:
            node: The ID of the node to get information about.

        Returns:
            Information about the node as a NodeInfo object.
        """
        ...
