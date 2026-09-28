import os
from uuid import uuid4

import pytest
from uncertainty_engine_resource_client.models import (
    PostProjectRecordRequest,
    ProjectRecordInput,
)
from uncertainty_engine_types import NodeInfo

from uncertainty_engine import Client, Environment
from uncertainty_engine.client import Job
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.nodes.basic import Add
from uncertainty_engine.nodes.workflow import Workflow


@pytest.fixture(scope="class")
def client() -> Client:
    """Fixture to initialize the Client class once per test class."""

    return Client(env="local")


@pytest.fixture(scope="module")
def e2e_client():
    """
    A Client instance for end-to-end testing.

    You _must_ set the following environment variables:

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
    client.authenticate()
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


@pytest.fixture(scope="module")
def project_id(e2e_client: Client):
    """
    A throwaway e2e test project, deleted along with its workflows after
    the tests.
    """
    projects_client = e2e_client.projects.projects_client
    project_record = ProjectRecordInput(
        name=f"sdk-e2e-{uuid4()}",
        owner_id=e2e_client.projects.account_id,
    )
    response = projects_client.post_project_record(
        PostProjectRecordRequest(project_record=project_record)
    )
    yield response.project_record.id
    projects_client.delete_project_record(response.project_record.id)


@pytest.fixture(scope="module")
def workflow_id(e2e_client: Client, project_id: str) -> str:
    """
    An e2e test workflow that adds 4 to the value of a number node (5).
    """
    number = Node(node_name="Number", version="0.2.0", label="num node", value="5")
    add = Add(lhs=4, rhs=number.make_handle("value"), label="add node")
    graph = Graph()
    graph.add_nodes_from([number, add])

    workflow = Workflow(
        graph=graph.nodes,
        inputs=graph.external_input,
        requested_output={"add result": add.make_handle("ans").model_dump()},
    )
    return e2e_client.workflows.save(
        project_id=project_id,
        workflow=workflow,
        workflow_name="e2e workflow",
    )


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
