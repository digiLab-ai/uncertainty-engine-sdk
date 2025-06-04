import os

import pytest

from uncertainty_engine import Client, Environment
from uncertainty_engine.client import Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.basic import Add


@pytest.fixture(scope="class")
def client() -> Client:
    """Fixture to initialize the Client class once per test class."""

    return Client(env="local")


@pytest.fixture(scope="module")
def e2e_client():
    """
    A Client instance for end-to-end testing.

    For the end-to-end tests to run successfully, the following environment
    variables must be set to describe the target environment:

    - `UE_ACCOUNT_ID`: The user's Resource Service account ID.
    - `UE_PASSWORD`: User account password.
    - `UE_USERNAME`: User account email.
    """

    client = Client(env="dev")
    client.authenticate(os.environ["UE_ACCOUNT_ID"])
    return client


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
