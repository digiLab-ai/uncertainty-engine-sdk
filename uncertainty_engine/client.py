from enum import Enum
from time import sleep
from typing import Optional, Union

import requests
from pydantic import BaseModel
from typeguard import typechecked

from uncertainty_engine.nodes.base import Node

DEFAULT_DEPLOYMENT = "http://localhost:8000/api"
STATUS_WAIT_TIME = 5  # An interval of 5 seconds to wait between status checks while waiting for a job to complete


# TDOO: Use the Enum class from the uncertainty_engine_types package.
class ValidStatus(Enum):
    """
    Represents the possible statuses fort a job in the Uncertainty Engine.
    """

    STARTED = "running"
    PENDING = "pending"
    SUCCESS = "completed"
    FAILURE = "failed"

    def is_terminal(self) -> bool:
        return self in [ValidStatus.SUCCESS, ValidStatus.FAILURE]


# TODO: Move this to the uncertainty_engine_types package.
class Job(BaseModel):
    """
    Represents a job in the Uncertainty Engine.
    """

    node_id: str
    job_id: str


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

    def list_nodes(self, category: Optional[str] = None) -> list:
        """
        List all available nodes in the specified deployment.

        Args:
            category: The category of nodes to list. If not specified, all nodes are listed.
                Defaults to ``None``.

        Returns:
            List of available nodes. Each list item is a dictionary of information about the node.
        """
        response = requests.get(f"{self.deployment}/nodes/list")
        nodes = response.json()
        node_list = [node_info for node_info in nodes.values()]

        if category is not None:
            node_list = [node for node in node_list if node["category"] == category]

        return node_list

    def queue_node(self, node: Union[str, Node], input: Optional[dict] = None) -> Job:
        """
        Queue a node for execution.

        Args:
            node: The name of the node to execute or the node object itself.
            input: The input data for the node. If the node is defined by its name,
                this is required. Defaults to ``None``.

        Returns:
            A Job object representing the queued job.
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
                "node_id": node,
                "inputs": input,
            },
        )

        job_id = response.json()

        return Job(node_id=node, job_id=job_id)

    def run_node(self, node: Union[str, Node], input: Optional[dict] = None) -> dict:
        """
        Run a node synchronously.

        Args:
            node: The name of the node to execute or the node object itself.
            input: The input data for the node. If the node is defined by its name,
                this is required. Defaults to ``None``.

        Returns:
            The output of the node.
        """
        job_id = self.queue_node(node, input)
        return self._wait_for_job(job_id)

    def job_status(self, job: Job) -> dict:
        """
        Check the status of a job.

        Args:
            job: The job to check.

        Returns:
            A dictionary containing the status of the job.
        """
        response = requests.get(
            f"{self.deployment}/nodes/status/{job.node_id}/{job.job_id}"
        )
        return response.json()

    def view_tokens(self) -> Optional[int]:
        """
        View how many tokens the user currently has available.

        Returns:
            Number of tokens the user currently has available.
        """

        # The token service for the new backend is not yet implemented.
        # This is a placeholder for when the service is implemented.
        # TODO: Make a request to the token service to get the user's token balance once it is implemented.
        # response = requests.get(f"{self.deployment}/tokens/user/{self.email}")
        tokens = 100

        return tokens

    def _wait_for_job(self, job: Job) -> dict:
        """
        Wait for a job to complete.

        Args:
            job: The job to wait for.

        Returns:
            The completed status of the job.
        """
        response = self.job_status(job)
        status = ValidStatus(response["status"])
        while not status.is_terminal():
            sleep(STATUS_WAIT_TIME)
            response = self.job_status(job)
            status = ValidStatus(response["status"])

        return response
