import pytest

from uncertainty_engine.client import Client
from uncertainty_engine.exceptions import NodeNotFoundError, NodeValidationError


class TestDynamicNodesE2E:

    def test_build_by_attribute(self, e2e_client: Client) -> None:
        """
        Verify that a node can be built by attribute against the live
        registry.

        Args:
            e2e_client: A Client instance.
        """

        node = e2e_client.nodes.Add(lhs=1, rhs=2, label="add")

        assert node.node_name == "Add"
        assert node() == ("Add", {"lhs": 1, "rhs": 2})

    def test_build_by_call(self, e2e_client: Client) -> None:
        """
        Verify that a node can be built by calling `nodes`.

        Args:
            e2e_client: A Client instance.
        """

        node = e2e_client.nodes("Add", lhs=1, rhs=2, label="add")

        assert node.node_name == "Add"

    def test_build_node_without_hand_written_class(self, e2e_client: Client) -> None:
        """
        Verify that a node with no hand-written class in the SDK can be
        built.

        Args:
            e2e_client: A Client instance.
        """

        # `Number` is chosen because the SDK ships no hand-written class
        # for it, so it can only have been built from the registry.
        node = e2e_client.nodes.Number(value="5", label="number")

        assert node.node_name == "Number"
        assert node.version

    def test_run_a_dynamically_built_node(self, e2e_client: Client) -> None:
        """
        Verify that a dynamically built node can actually be run.

        Args:
            e2e_client: A Client instance.
        """

        node = e2e_client.nodes.Add(lhs=1, rhs=2, label="add")
        job_info = e2e_client.run_node(node)

        assert job_info.outputs["ans"] == 3.0

    def test_invalid_inputs_raise(self, e2e_client: Client) -> None:
        """
        Verify that inputs are validated against the live schema.

        Args:
            e2e_client: A Client instance.
        """

        with pytest.raises(NodeValidationError):
            e2e_client.nodes.Add(lhs=1, not_an_input=2, label="add")

    def test_unknown_node_raises(self, e2e_client: Client) -> None:
        """
        Verify that an unknown node raises `NodeNotFoundError`.

        Args:
            e2e_client: A Client instance.
        """

        with pytest.raises(NodeNotFoundError) as exc_info:
            e2e_client.nodes.NodeThatDoesNotExist(label="nope")

        assert "available()" in str(exc_info.value)

    def test_available_and_describe(self, e2e_client: Client) -> None:
        """
        Verify that the catalogue can be listed and a node described.

        Args:
            e2e_client: A Client instance.
        """

        available = e2e_client.nodes.available()

        assert "Add" in available
        assert available == sorted(available)

        info = e2e_client.nodes.describe("Add")

        assert info.inputs
        assert info.outputs

    def test_with_versions_pins_only_listed_nodes(self, e2e_client: Client) -> None:
        """
        Verify that a pinned view uses the pinned version, that unlisted
        nodes use the default, and that the default view is unaffected.

        Args:
            e2e_client: A Client instance.
        """

        version = e2e_client.get_node_versions("Add")[0]
        pinned = e2e_client.nodes.with_versions({"Add": version})

        assert pinned.Add(lhs=1, rhs=2, label="add").version == version

        # An unlisted node resolves to the registry's default.
        assert pinned.Number(value="5", label="number").version

        # A per-call version still wins.
        assert pinned.Add(lhs=1, rhs=2, label="add", version=version).version == version

        # The default view is untouched.
        assert e2e_client.nodes is not pinned
