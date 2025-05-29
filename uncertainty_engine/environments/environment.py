from __future__ import annotations

import importlib.resources
from json import load

from pydantic import BaseModel


class Environment(BaseModel):
    """
    An Uncertainty Engine environment.
    """

    cognito_user_pool_client_id: str
    """
    Cognito User Pool Application Client to authenticate with.
    """

    core_api: str
    """
    Core API URL.
    """

    region: str
    """
    Amazon Web Services region where the environment is deployed.
    """

    resource_api: str
    """
    Resource Service API.
    """

    @classmethod
    def get(cls, name: str) -> Environment:
        """
        Gets a named Uncertainty Engine environment.

        Args:
            name: Environment name.

        Returns:
            Uncertainty Engine environment.

        Raises:
            LookupError: Raised if the specified environment does not exist.
        """

        environments_path = "uncertainty_engine.environments"
        environment_filename = f"{name}.json"

        environments = importlib.resources.files(environments_path)
        file = environments / environment_filename

        try:
            with file.open("r") as f:
                values = load(f)
                return Environment(**values)

        except FileNotFoundError as ex:
            raise LookupError(f'Environment "{name}" not found') from ex
