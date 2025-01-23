from typing import Optional, Union

import requests
from typeguard import typechecked

from uncertainty_engine.nodes.base import Node

DEFAULT_DEPLOYMENT = "http://localhost:8000/api"


@typechecked
class Client:
    def __init__(self, email: str, deployment: str = DEFAULT_DEPLOYMENT):
        """
        A client for interacting with the Uncertainty Engine.

        Args:
            email: The email address of the user.
            deployment: The URL of the Uncertainty Engine deployment.
        """
        self.email = email
        self.deployment = deployment

    def list_nodes(self) -> list:
        """
        List all available nodes in the specified deployment.

        Returns:
            List of available nodes. Each list item is a dictionary information about the node.
        """
        response = requests.get(f"{self.deployment}/nodes/list")
        return response.json()

    def queue_node(self, node: Union[str, Node], input: Optional[dict] = None) -> str:
        """
        Queue a node for execution.

        Args:
            node: The name of the node to execute or the node object itself.
            input: The input data for the node. If the node is defined by its name,
                this is required. Defaults to ``None``.

        Returns:
            The job ID of the queued node.
        """
        if isinstance(node, Node):
            node, input = node()
        elif isinstance(node, str) and input is None:
            raise ValueError(
                "Input data/parameters are required when specifying a node by name."
            )

        response = requests.post(
            f"{self.deployment}/nodes/queue",
            json={
                "email": self.email,
                "node": node,
                "input": input,
            },
        )
        return response.json()

    def job_status(self, job_id: str) -> dict:
        """
        Check the status of a job.

        Args:
            job_id: The ID of the job to check.

        Returns:
            A dictionary containing the status of the job.
        """
        response = requests.get(f"{self.deployment}/nodes/status/{job_id}")
        return response.json()

    def view_tokens(self) -> Optional[int]:
        """
        View how many tokens the user currently has available.

        Returns:
            Number of tokens the user currently has available.
        """

        response = requests.get(f"{self.deployment}/tokens/user/{self.email}")
        return response.json()
