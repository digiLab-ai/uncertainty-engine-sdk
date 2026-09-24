import warnings
from typing import Any, Callable

from requests import HTTPError
from typeguard import typechecked
from uncertainty_engine_types import NodeInfo

from uncertainty_engine.exceptions import NodeNotFoundError
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.protocols import Client

Version = str | int


@typechecked
class DynamicNodes:
    """
    Build any node by name, resolving its schema from the Node Registry
    on demand.

    Node schemas are fetched one node at a time, as they are needed; the
    catalogue is never loaded up front. Resolved schemas and the
    catalogue are cached on the client, so every view - pinned or not,
    and whenever it was created - shares them.

    Args:
        client: The client used to resolve node information.
        versions: Optional mapping of node ID to the version to pin it
            to. Nodes that are absent from the mapping resolve to the
            registry's default version. Defaults to `None`.

    Example:
        >>> client.nodes.Add(lhs=1, rhs=2, label="add")
        >>> client.nodes("Add", lhs=1, rhs=2, label="add")
        >>> client.nodes.available()
        >>> client.nodes.describe("Add").inputs
    """

    def __init__(
        self,
        client: Client,
        versions: dict[str, Version] | None = None,
    ) -> None:
        self._client = client
        self._versions: dict[str, Version] = dict(versions) if versions else {}

    def __call__(
        self,
        node: str,
        label: str | None = None,
        version: Version | None = None,
        **inputs: Any,
    ) -> Node:
        """
        Build a node by name.

        Args:
            node: The ID of the node to build.
            label: A human-readable label for the node. Defaults to
                `None`.
            version: The version of the node to build. Takes precedence
                over any pinned version. Defaults to `None`, meaning the
                pinned version is used, or the registry's default when
                the node is not pinned.
            **inputs: The node's input parameters.

        Returns:
            The built node.

        Raises:
            NodeNotFoundError: If the node (or the requested version of
                it) does not exist.
            NodeValidationError: If the inputs do not satisfy the node's
                schema.

        Example:
            >>> add = client.nodes("Add", lhs=1, rhs=2, label="add")
        """

        node_info = self._resolve(node, version)

        # `Node` fetches its own `node_info` whenever it is given a
        # client, which would bypass the cache and repeat the request we
        # have just made. Build it without a client instead, then supply
        # the information we already hold. `client` and `node_info` are
        # both excluded from a node's inputs, so assigning them here
        # does not affect the built node's inputs.
        with warnings.catch_warnings():
            # Suppress the "a `client` is required" warning; a client is
            # available, it is just attached after construction.
            warnings.simplefilter("ignore", UserWarning)

            built = Node(
                node_name=node,
                version=node_info.version_node,
                label=label,
                **inputs,
            )

        built.client = self._client
        built.node_info = node_info
        built.validate()

        return built

    def __getattr__(self, node: str) -> Callable[..., Node]:
        """
        Return a builder for the node of the given name.

        Accessing an attribute performs no request; the node's schema is
        resolved when the builder is called.

        Args:
            node: The ID of the node to build.

        Returns:
            A callable that builds the node.

        Example:
            >>> add = client.nodes.Add(lhs=1, rhs=2, label="add")
        """

        # Never treat private or dunder lookups as node names; they are
        # made by `copy`, `pickle` and interactive shells, which expect
        # an `AttributeError` rather than a node builder.
        if node.startswith("_"):
            raise AttributeError(node)

        def build(**kwargs: Any) -> Node:
            return self(node, **kwargs)

        build.__name__ = node
        build.__doc__ = (
            f"Build a `{node}` node. Accepts `label`, `version` and the "
            f"node's inputs. See `describe('{node}')` for its schema."
        )

        return build

    def __dir__(self) -> list[str]:
        """
        List this object's attributes along with the available node
        names, so that nodes can be tab-completed.

        Returns:
            Attribute and node names.
        """

        names = set(super().__dir__())

        try:
            names.update(self.available())
        except Exception:
            # Interactive shells build their completion list from
            # `dir()`, so this must never raise: an unreachable or
            # unauthenticated registry simply contributes no names.
            pass

        return sorted(names)

    def available(self) -> list[str]:
        """
        List the IDs of all available nodes.

        This is the only operation that loads the catalogue; building a
        node does not. The client caches the catalogue, and loading it
        also seeds the schema of every node it returns at the version
        listed, so building a listed node pinned to that version makes
        no further request.

        Returns:
            The IDs of all available nodes, sorted.

        Example:
            >>> client.nodes.available()
            ['Add', 'Display', 'Number', ...]
        """

        return sorted(node["id"] for node in self._client.list_nodes() if "id" in node)

    def describe(
        self,
        node: str,
        version: Version | None = None,
    ) -> NodeInfo:
        """
        Describe a node, including its inputs and outputs.

        Args:
            node: The ID of the node to describe.
            version: The version of the node to describe. Takes
                precedence over any pinned version. Defaults to `None`,
                meaning the pinned version is used, or the registry's
                default when the node is not pinned.

        Returns:
            Information about the node as a `NodeInfo` object.

        Raises:
            NodeNotFoundError: If the node (or the requested version of
                it) does not exist.

        Example:
            >>> info = client.nodes.describe("Add")
            >>> print(info.inputs)
            >>> print(info.outputs)
        """

        return self._resolve(node, version)

    def with_versions(self, versions: dict[str, Version]) -> "DynamicNodes":
        """
        Return a version-pinned view of the available nodes.

        The listed nodes resolve to the given versions; every other node
        resolves to the registry's default version. A `version` passed
        when building a node still takes precedence, so the order of
        precedence is: call argument, then this mapping, then the
        registry's default.

        The view is a separate object. This object is left unchanged.

        Args:
            versions: Mapping of node ID to the version to pin it to.
                Merged over any versions already pinned on this object.

        Returns:
            A new `DynamicNodes` pinned to the given versions. Schemas
            and the catalogue are cached on the client, so the view
            shares them however it was made.

        Example:
            >>> pinned = client.nodes.with_versions({"Add": "0.2.0"})
            >>> pinned.Add(lhs=1, rhs=2, label="add")  # version 0.2.0
            >>> client.nodes.Add(lhs=1, rhs=2, label="add")  # default
        """

        return DynamicNodes(self._client, versions={**self._versions, **versions})

    def _resolve(self, node: str, version: Version | None = None) -> NodeInfo:
        """
        Resolve a node's information.

        The client caches what it resolves, so asking twice for the same
        node and version makes one request.

        Args:
            node: The ID of the node to resolve.
            version: The requested version, which takes precedence over
                any pinned version. Defaults to `None`.

        Returns:
            Information about the node as a `NodeInfo` object.

        Raises:
            NodeNotFoundError: If the node (or the requested version of
                it) does not exist.
        """

        resolved_version = version if version is not None else self._versions.get(node)

        try:
            if resolved_version is None:
                node_info = self._client.get_default_node_info(node)
            else:
                # `get_node_info` signals an absent node or version
                # this way. Scoped to this branch because
                # `get_default_node_info` makes no such promise, so a
                # `KeyError` from it is a real fault, not a miss.
                try:
                    node_info = self._client.get_node_info(
                        node,
                        resolved_version,
                    )
                except KeyError as error:
                    raise NodeNotFoundError(node, resolved_version) from error
        except HTTPError as error:
            response = error.response

            if response is None or response.status_code != 404:
                # Only a confirmed 404 means the node is missing from the
                # registry; anything else (including an error with no
                # response, e.g. a connection failure) is a real failure
                # and is reported as-is.
                raise

            raise NodeNotFoundError(node, resolved_version) from error

        return node_info
