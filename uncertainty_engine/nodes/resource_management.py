from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import ResourceID, S3Storage

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion


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


@typechecked
class LoadModel(Node):
    """
    Load a model from the Uncertainty Engine resource management
    system.
    """

    project_id: str
    """The ID of the project containing the model."""

    file_id: dict[str, str]
    """The ID of the model to load."""

    label: str | None
    """
    A human-readable label for the node. This should be unique to all
    other node labels in a workflow.
    """

    node_name: str = "LoadModel"
    """The node ID."""

    def __init__(
        self,
        project_id: str,
        file_id: str,
        label: str | None = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            project_id=project_id,
            file_id=ResourceID(id=file_id).model_dump(),
        )


@typechecked
class Save(Node):
    """
    Save a resource in the Uncertainty Engine resource management
    system.

    Note that this is for saving resources that are output by a node.
    If you wish to upload a file to use in your workflow then you should
    use the resource provider (use `client.resources.upload()` to upload
    a local resource to the Uncertainty Engine).
    """

    data: HandleUnion[S3Storage]
    """A reference to the node output data to be saved."""

    file_id: str
    """
    The human-readable name for the saved resource. If a resource of the
    same type and name already exists, the save node will create a new
    version of that existing resource.
    """

    project_id: str
    """The ID of the project to save to."""

    label: str | None
    """
    A human-readable label for the node. This should be unique to all
    other node labels in a workflow.
    """

    node_name: str = "Save"
    """The node ID."""

    def __init__(
        self,
        data: HandleUnion[S3Storage],
        file_name: str,
        project_id: str,
        label: str | None = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            data=data,
            # NOTE: The underlying node input ID for the file name is
            # `file_id`, but we refer to it as `file_name` in this class
            # for clarity and ease of use.
            file_id=file_name,
            project_id=project_id,
        )
