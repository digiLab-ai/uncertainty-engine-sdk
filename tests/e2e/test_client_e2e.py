import os

import pytest


@pytest.mark.parametrize(
    "test_user_email, deployment_url",
    [(os.environ["UE_USER_EMAIL"], os.environ["UE_DEPLOYMENT_URL"])],
    indirect=True,
)
def test_list_nodes(client):
    """
    Verify that the list_nodes method can be poked successfully.

    Args:
        client: A Client instance.
    """
    nodes = client.list_nodes()
    print(nodes)
