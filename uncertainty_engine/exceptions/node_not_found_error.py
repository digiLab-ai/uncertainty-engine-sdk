class NodeNotFoundError(Exception):
    """
    Raised when a node cannot be found in the Node Registry.

    Args:
        node: The ID of the node that could not be found.
        version: The version that was requested, if one was pinned.
            Defaults to `None`, meaning the registry's default version
            was requested.
    """

    def __init__(self, node: str, version: str | int | None = None) -> None:
        self.node = node
        """The ID of the node that could not be found."""

        self.version = version
        """The version that was requested, if one was pinned."""

        described = (
            f"Node '{node}'"
            if version is None
            else f"Node '{node}' with version '{version}'"
        )

        super().__init__(
            f"{described} was not found. "
            "Use `client.nodes.available()` to see the available nodes."
        )
