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

    def test_seeded_schema_matches_a_direct_lookup(self, e2e_client: Client) -> None:
        """
        Verify that the schema seeded by `available()` is the same one a
        direct lookup returns.

        The catalogue and the single-node endpoint each choose a node's
        default version by their own logic, so this guards against the
        seeded schema drifting from the one a build would otherwise have
        used, and against the catalogue seeding an incomplete schema.

        Args:
            e2e_client: A Client instance.
        """

        e2e_client.nodes.available()

        seeded = e2e_client.nodes.describe("Add")

        e2e_client.clear_node_cache()

        fetched = e2e_client.nodes.describe("Add")

        assert seeded.outputs
        assert seeded.version_node == fetched.version_node
        assert seeded == fetched

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
