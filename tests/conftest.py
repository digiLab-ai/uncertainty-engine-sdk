import os

import pytest

from uncertainty_engine import Environment
from uncertainty_engine.client import Client, Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.basic import Add


@pytest.fixture(scope="class")
def test_user_email(request):
    """
    An email address for testing.
    """
    return getattr(request, "param", "a.user@digilab.co.uk")


@pytest.fixture(scope="class")
def deployment_url(request):
    """
    The deployment URL for the Uncertainty Engine service.
    """
    return getattr(request, "param", Environment.get("local").core_api)


@pytest.fixture(scope="class")
def client(test_user_email: str) -> Client:
    """Fixture to initialize the Client class once per test class."""
    return Client(test_user_email, Environment.get("local"))


@pytest.fixture(scope="module")
def e2e_client():
    """
    A Client instance for end-to-end testing.

    NOTE: For the e2e tests to run successfully, the following environment variables must be set:

        UE_USER_EMAIL: A user email that has been registered with the Uncertainty Engine service.
        UE_DEPLOYMENT_URL: The deployment URL for the Uncertainty Engine service.
    """
    return Client(
        os.environ["UE_USER_EMAIL"],
        "dev",
    )


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
