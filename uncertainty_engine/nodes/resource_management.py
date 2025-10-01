from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import ResourceID

from uncertainty_engine.nodes.base import Node


@typechecked
class LoadDataset(Node):
    """
    Load a dataset from the Uncertainty Engine resource management
    system.

    Args:
       project_id: The ID of the project containing the dataset.
       file_id: The ID of the dataset file to load.
       label: A human-readable label for the node. Defaults to None.
    """

    node_name: str = "LoadDataset"

    def __init__(
        self,
        project_id: str,
        file_id: str,
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            project_id=project_id,
            file_id=ResourceID(id=file_id).model_dump(),
        )
        self.project_id = project_id
        self.label = label
