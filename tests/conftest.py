import pytest
from uncertainty_engine_types import NodeInfo

from uncertainty_engine import Client
from uncertainty_engine.client import Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.basic import Add


@pytest.fixture(scope="class")
def client() -> Client:
    """Fixture to initialize the Client class once per test class."""

    return Client(env="local")


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
    add = Add(lhs=1, rhs=2)
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
