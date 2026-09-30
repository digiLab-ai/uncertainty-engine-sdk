import os
from uuid import uuid4

import pytest
from uncertainty_engine_resource_client.models import (
    PostProjectRecordRequest,
    ProjectRecordInput,
)

from uncertainty_engine import Client, Environment
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.nodes.basic import Add
from uncertainty_engine.nodes.workflow import Workflow


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
