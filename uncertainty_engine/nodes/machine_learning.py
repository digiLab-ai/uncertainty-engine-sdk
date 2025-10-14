from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import CSVDataset, ModelConfig

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion


@typechecked
class TrainModel(Node):
    """
    Train a Gaussian Process model using the Uncertainty Engine.

    Args:
        config: A reference to the model configuration to use for training.
        inputs: A reference to the input dataset for training the model.
        outputs: A reference to the output dataset for training the model.
        label: A human-readable label for the node. This should be unique to all
               other node labels in a workflow. Defaults to "Train Model".
        project_id: The ID of the project to associate with this node.
    """

    node_name: str = "TrainModel"
    """The node ID."""

    label: str = "Train Model"
    """A human-readable label for the node."""

    config: HandleUnion[ModelConfig]
    """A reference to the model configuration to use for training."""

    inputs: HandleUnion[CSVDataset]
    """A reference to the input dataset for training the model."""

    outputs: HandleUnion[CSVDataset]
    """A reference to the output dataset for training the model."""

    project_id: Optional[str] = None
    """The ID of the project to associate with this node."""

    def __init__(
        self,
        config: HandleUnion[ModelConfig],
        inputs: HandleUnion[CSVDataset],
        outputs: HandleUnion[CSVDataset],
        label: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label or self.label,
            config=config,
            inputs=inputs,
            outputs=outputs,
            project_id=project_id,
        )
