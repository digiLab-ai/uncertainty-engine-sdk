import os

import pytest

from uncertainty_engine import Client, Environment
from uncertainty_engine.client import Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.basic import Add


@pytest.fixture(scope="class")
def client() -> Client:
    """Fixture to initialize the Client class once per test class."""
    return Client(
        env=Environment.get("local"),
    )


@pytest.fixture(scope="module")
def e2e_client():
    """
    A Client instance for end-to-end testing.

    For the end-to-end tests to run successfully, the following environment
    variables must be set to describe the target environment:

    - `UE_USERNAME`: A user email that has been registered with the Uncertainty
        Engine service.
    - `UE_COGNITO_CLIENT_ID`: Cognito User Pool Application Client ID.
    - `UE_CORE_API`: Core API endpoint. Must start with a protocol (i.e.
        "https://") and must not end with a slash.
    - `UE_REGION`: Amazon Web Services region.
    - `UE_RESOURCE_API`: Resource API endpoint. Must start with a protocol (i.e.
        "https://") and must not end with a slash.
    """

    return Client(
        env=Environment(
            cognito_user_pool_client_id=os.environ["UE_COGNITO_CLIENT_ID"],
            core_api=os.environ["UE_CORE_API"],
            region=os.environ["UE_REGION"],
            resource_api=os.environ["UE_RESOURCE_API"],
        ),
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
