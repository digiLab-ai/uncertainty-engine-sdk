import pytest
from uncertainty_engine_types import NodeInfo

from uncertainty_engine import Client
from uncertainty_engine.client import Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node


@pytest.fixture(scope="class")
def client() -> Client:
    """Fixture to initialize the Client class once per test class."""

    return Client(env="local")


@pytest.fixture(autouse=True)
def clear_node_cache(request):
    """
    Empty the client's node cache before each test.

    `client` is class-scoped and `e2e_client` module-scoped, and node
    schemas and the catalogue are cached on the client for its
    lifetime, so without this a schema resolved by one test would be
    reused by the next. Only tests that actually take one of those
    fixtures are affected.
    """

    for name in ("client", "e2e_client"):
        if name in request.fixturenames:
            request.getfixturevalue(name).clear_node_cache()


@pytest.fixture(scope="class")
def simple_node_label():
    """
    A simple node label.
    """
    return "add"


@pytest.fixture(scope="class")
def simple_graph(simple_node_label):
    """
    A simple graph with a single node.
    """
    graph = Graph()
    add = Node(node_name="Add", version="0.2.0", lhs=1, rhs=2)
    graph.add_node(add, simple_node_label)
    return graph


@pytest.fixture()
def mock_job():
    """
    A mock Job.
    """
    return Job(node_id="node_a", job_id="job_a")


@pytest.fixture
def default_node_info() -> NodeInfo:
    """
    Provide a default NodeInfo object for tests.
    """
    return NodeInfo(
        id="default_id",
        label="default_label",
        category="default_category",
        description="default_description",
        long_description="default_long_description",
        image_name="default_image",
        cost=0,
        version_base_image=1,
        version_node=1,
        inputs={},
        outputs={},
    )
