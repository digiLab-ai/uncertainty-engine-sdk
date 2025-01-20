from typing import Optional

import requests
from typeguard import typechecked

DEFAULT_DEPLOYMENT = "http://localhost:8000/api"


@typechecked
class Client:
    def __init__(self, email: str, deployment: str = DEFAULT_DEPLOYMENT):
        self.email = email
        self.deployment = deployment

    def list_nodes(self) -> list:
        response = requests.get(f"{self.deployment}/nodes/list")
        return response.json()

    def run_node(self, node: str, input: dict) -> dict:
        response = requests.post(
            f"{self.deployment}/nodes/run",
            json={
                "email": self.email,
                "node": node,
                "input": input,
            },
        )
        return response.json()

    def queue_node(self, node: str, input: dict) -> str:
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
        response = requests.get(f"{self.deployment}/nodes/status/{job_id}")
        return response.json()

    def view_tokens(self) -> Optional[int]:
        """
        View how many tokens the user currently has available.

        Returns:
            int: Number of tokens the user currently has available.
        """

        response = requests.get(f"{self.deployment}/tokens/user/{self.email}")
        return response.json()
