from typing import Any
from unittest.mock import Mock

import pytest
from requests import HTTPError

from tests.mock_api_invoker import mock_core_api
from uncertainty_engine import Client
from uncertainty_engine.dynamic_nodes import DynamicNodes
from uncertainty_engine.exceptions import NodeNotFoundError, NodeValidationError
from uncertainty_engine.nodes.base import Node


def node_info_dict(node_id: str, version: str | int = "latest") -> dict[str, Any]:
    """
    Build a `NodeInfo` response body for a two-input node.

    Args:
        node_id: The ID of the node.
        version: The node's version.

    Returns:
        A `NodeInfo` shaped dictionary.
    """
    return {
        "id": node_id,
        "label": node_id,
        "category": "test_category",
        "description": "A test node",
        "long_description": "A long description for the test node.",
        "image_name": "test_image.png",
        "cost": 0,
        "inputs": {
            "lhs": {"type": "float", "label": "LHS", "description": "Left"},
            "rhs": {"type": "float", "label": "RHS", "description": "Right"},
        },
        "outputs": {
            "ans": {"type": "float", "label": "Answer", "description": "Result"},
        },
        "version_base_image": 1,
        "version_node": version,
    }


def http_error(status_code: int) -> HTTPError:
    """
    Build an `HTTPError` carrying the given status code.

    Args:
        status_code: The HTTP status code.

    Returns:
        An `HTTPError`.
    """
    response = Mock()
    response.status_code = status_code
    response.reason = "Not Found" if status_code == 404 else "Server Error"
    return HTTPError(response=response)


@pytest.fixture
def nodes(client: Client) -> DynamicNodes:
    """
    A fresh `DynamicNodes` for each test.

    `client` is class-scoped, and a `DynamicNodes` caches for the life
    of its client, so tests would otherwise share resolved schemas.
    """
    return DynamicNodes(client)


class TestBuilding:

    def test_attribute_style_fetches_only_that_node(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that building a node by attribute fetches only that
        node's schema, and does not load the catalogue.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            node = nodes.Add(lhs=1, rhs=2, label="add")

        assert isinstance(node, Node)
        assert node.node_name == "Add"
        assert node() == ("Add", {"lhs": 1, "rhs": 2})

    def test_call_style(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a node can be built by calling `nodes` directly.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            node = nodes("Add", lhs=1, rhs=2, label="add")

        assert node.node_name == "Add"
        assert node.label == "add"

    def test_version_comes_from_the_resolved_schema(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that the built node carries the version the registry
        resolved, rather than one worked out by the SDK.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add", version="0.9.1"))

            node = nodes.Add(lhs=1, rhs=2, label="add")

        assert node.version == "0.9.1"

    def test_int_only_version(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a node whose only version is an integer can be
        built.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Tool", node_info_dict("Tool", version=0))

            node = nodes.Tool(lhs=1, rhs=2, label="tool")

        assert node.version == 0

    def test_schema_is_cached(self, client: Client, nodes: DynamicNodes):
        """
        Verify that building the same node twice resolves its schema
        once.
        """
        with mock_core_api(client) as api:
            # A single expectation; a second request would fail the mock.
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            first = nodes.Add(lhs=1, rhs=2, label="one")
            second = nodes.Add(lhs=3, rhs=4, label="two")

        assert first.node_info is second.node_info


class TestValidation:

    def test_unknown_input_raises(self, client: Client, nodes: DynamicNodes):
        """
        Verify that inputs are validated against the live schema.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            with pytest.raises(NodeValidationError) as exc_info:
                nodes.Add(lhs=1, nope=2, label="add")

        assert "nope" in str(exc_info.value)

    def test_missing_required_input_raises(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a missing required input raises.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            with pytest.raises(NodeValidationError) as exc_info:
                nodes.Add(lhs=1, label="add")

        assert "rhs" in str(exc_info.value)


class TestNodeNotFound:

    def test_unknown_node_raises_node_not_found(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that an unknown node raises `NodeNotFoundError`, pointing
        at `available()`.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Nope", http_error(404))

            with pytest.raises(NodeNotFoundError) as exc_info:
                nodes.Nope(lhs=1, rhs=2, label="nope")

        assert exc_info.value.node == "Nope"
        assert exc_info.value.version is None
        assert "available()" in str(exc_info.value)

    def test_unknown_pinned_version_raises_node_not_found(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that a pinned version that does not exist raises
        `NodeNotFoundError` naming the version.
        """
        pinned = nodes.with_versions({"Add": "9.9.9"})

        with mock_core_api(client) as api:
            api.expect_post("/nodes/query", response=KeyError("Add@9.9.9"))

            with pytest.raises(NodeNotFoundError) as exc_info:
                pinned.Add(lhs=1, rhs=2, label="add")

        assert exc_info.value.version == "9.9.9"
        assert "9.9.9" in str(exc_info.value)
        assert "get_node_versions" in str(exc_info.value)

    def test_non_404_error_is_not_reported_as_missing(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that a non-404 HTTP error propagates rather than being
        mislabelled as a missing node.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", http_error(500))

            with pytest.raises(HTTPError) as exc_info:
                nodes.Add(lhs=1, rhs=2, label="add")

        assert exc_info.value.response.status_code == 500

    def test_response_less_error_is_not_reported_as_missing(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that an HTTP error with no attached response propagates
        rather than being mislabelled as a missing node (there is no 404
        evidence).
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", HTTPError(response=None))

            with pytest.raises(HTTPError) as exc_info:
                nodes.Add(lhs=1, rhs=2, label="add")

        assert exc_info.value.response is None


class TestDiscovery:

    def test_available(self, client: Client, nodes: DynamicNodes):
        """
        Verify that `available` lists all node names.
        """
        with mock_core_api(client) as api:
            api.expect_get(
                "/nodes/list",
                {
                    "Add": {"id": "Add", "category": "Basic"},
                    "Number": {"id": "Number", "category": "Basic"},
                },
            )

            names = nodes.available()

        assert names == ["Add", "Number"]

    def test_available_is_cached(self, client: Client, nodes: DynamicNodes):
        """
        Verify that the catalogue is loaded once.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/list", {"Add": {"id": "Add"}})

            nodes.available()
            names = nodes.available()

        assert names == ["Add"]

    def test_available_returns_a_copy(self, client: Client, nodes: DynamicNodes):
        """
        Verify that mutating the returned list does not corrupt the
        cache.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/list", {"Add": {"id": "Add"}})

            nodes.available().append("Mutated")
            names = nodes.available()

        assert names == ["Add"]

    def test_dir_includes_node_names(self, client: Client, nodes: DynamicNodes):
        """
        Verify that node names are offered for tab completion.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/list", {"Add": {"id": "Add"}})

            names = dir(nodes)

        assert "Add" in names
        assert "available" in names

    def test_dir_survives_an_unreachable_registry(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that tab completion does not raise when the catalogue
        cannot be loaded.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/list", http_error(500))

            names = dir(nodes)

        assert "available" in names

    def test_describe(self, client: Client, nodes: DynamicNodes):
        """
        Verify that `describe` returns the node's inputs and outputs.
        """
        with mock_core_api(client) as api:
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            info = nodes.describe("Add")

        assert sorted(info.inputs) == ["lhs", "rhs"]
        assert sorted(info.outputs) == ["ans"]

    def test_private_attributes_are_not_nodes(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that private lookups raise `AttributeError`, so that
        `copy`, `pickle` and interactive shells behave.
        """
        with pytest.raises(AttributeError):
            nodes._repr_html_


class TestWithVersions:

    def test_pins_listed_nodes(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a pinned node is resolved at the pinned version.
        """
        pinned = nodes.with_versions({"Add": "0.2.0"})

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/query",
                response={"Add@0.2.0": node_info_dict("Add", version="0.2.0")},
            )

            node = pinned.Add(lhs=1, rhs=2, label="add")

        assert node.version == "0.2.0"

    def test_unlisted_nodes_use_the_default(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a node absent from the mapping resolves to the
        registry's default version.
        """
        pinned = nodes.with_versions({"Add": "0.2.0"})

        with mock_core_api(client) as api:
            api.expect_get("/nodes/Number", node_info_dict("Number", version="latest"))

            node = pinned.Number(lhs=1, rhs=2, label="number")

        assert node.version == "latest"

    def test_call_version_overrides_the_map(self, client: Client, nodes: DynamicNodes):
        """
        Verify that a version passed when building takes precedence over
        the pinned version.
        """
        pinned = nodes.with_versions({"Add": "0.2.0"})

        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/query",
                response={"Add@0.3.0": node_info_dict("Add", version="0.3.0")},
            )

            node = pinned.Add(lhs=1, rhs=2, label="add", version="0.3.0")

        assert node.version == "0.3.0"

    def test_call_version_overrides_the_default_view(
        self, client: Client, nodes: DynamicNodes
    ):
        """
        Verify that a version passed when building is used even when
        nothing is pinned.
        """
        with mock_core_api(client) as api:
            api.expect_post(
                "/nodes/query",
                response={"Add@0.2.0": node_info_dict("Add", version="0.2.0")},
            )

            node = nodes.Add(lhs=1, rhs=2, label="add", version="0.2.0")

        assert node.version == "0.2.0"

    def test_returns_a_separate_view(self, client: Client, nodes: DynamicNodes):
        """
        Verify that pinning returns a new view and leaves the view it
        was made from unpinned.
        """
        pinned = nodes.with_versions({"Add": "0.2.0"})

        assert isinstance(pinned, DynamicNodes)
        assert pinned is not nodes
        assert nodes._versions == {}

        with mock_core_api(client) as api:
            # The original view still resolves the default version.
            api.expect_get("/nodes/Add", node_info_dict("Add"))

            node = nodes.Add(lhs=1, rhs=2, label="add")

        assert node.version == "latest"

    def test_pins_are_merged_when_chained(self, client: Client, nodes: DynamicNodes):
        """
        Verify that chaining `with_versions` merges the mappings.
        """
        pinned = nodes.with_versions({"Add": "0.2.0"}).with_versions(
            {"Number": "1.0.0"}
        )

        assert pinned._versions == {"Add": "0.2.0", "Number": "1.0.0"}


class TestClientWiring:

    def test_nodes_is_a_cached_dynamic_nodes(self):
        """
        Verify that `client.nodes` is a `DynamicNodes` and that the same
        object is returned each time, so its cache is not discarded.
        """
        client = Client(env="local")

        assert isinstance(client.nodes, DynamicNodes)
        assert client.nodes is client.nodes

    def test_with_versions_leaves_client_nodes_untouched(self):
        """
        Verify that taking a pinned view does not change the default
        `client.nodes`.
        """
        client = Client(env="local")
        default = client.nodes

        default.with_versions({"Add": "0.2.0"})

        assert client.nodes is default
        assert default._versions == {}
