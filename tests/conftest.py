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

    You _must_ set the following environment variables:

    - `UE_ACCOUNT_ID`: The user's Resource Service account ID.
    - `UE_PASSWORD`: User account password.
    - `UE_USERNAME`: User account email.

    In addition, you must set _either_ `UE_ENVIRONMENT` to the name of the
    environment to test or all of the following:

    - `UE_COGNITO_CLIENT_ID`: Cognito User Pool Application Client ID.
    - `UE_CORE_API`: Core API endpoint.
    - `UE_REGION`: Region where the environment is deployed.
    - `UE_RESOURCE_API`: Resource API endpoint.
    """

    env = os.environ.get("UE_ENVIRONMENT") or Environment(
        cognito_user_pool_client_id=os.environ["UE_COGNITO_CLIENT_ID"],
        core_api=os.environ["UE_CORE_API"],
        region=os.environ["UE_REGION"],
        resource_api=os.environ["UE_RESOURCE_API"],
    )

    client = Client(env=env)
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
