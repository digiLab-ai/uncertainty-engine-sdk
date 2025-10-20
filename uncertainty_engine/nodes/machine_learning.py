from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import ModelConfig, S3Storage

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion


@typechecked
class TrainModel(Node):
    """
    Train a Gaussian Process model using the Uncertainty Engine.

    Args:
        config: A `ModelConfig` for a machine learning model.
        inputs: A reference to the input dataset for training the model.
        outputs: A reference to the output dataset for training the
            model.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
        project_id: The ID of the project to associate with this node.
    """

    node_name: str = "TrainModel"
    """The node ID."""

    label: str = "Train Model"
    """A human-readable label for the node."""

    config: HandleUnion[ModelConfig]
    """A `ModelConfig` for a machine learning model."""

    inputs: HandleUnion[S3Storage]
    """A reference to the input dataset for training the model."""

    outputs: HandleUnion[S3Storage]
    """A reference to the output dataset for training the model."""

    project_id: Optional[str] = None
    """The ID of the project to associate with this node."""

    def __init__(
        self,
        config: HandleUnion[ModelConfig],
        inputs: HandleUnion[S3Storage],
        outputs: HandleUnion[S3Storage],
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


@typechecked
class PredictModel(Node):
    """
    Run predictions using a trained machine-learning model in the
    Uncertainty Engine.

    Args:
        model: A reference to the trained machine-learning model to use
            for prediction.
        inputs: A reference to the input dataset for making predictions.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
        project_id: The ID of the project to associate with this node.
    """

    node_name: str = "PredictModel"
    """The node ID."""

    label: str = "Predict Model"
    """A human-readable label for the node."""

    model: HandleUnion[S3Storage]
    """
    A reference to the trained machine-learning model to use for
    prediction.
    """

    dataset: HandleUnion[S3Storage]
    """A reference to the input dataset for making predictions."""

    project_id: Optional[str] = None
    """The ID of the project to associate with this node."""

    def __init__(
        self,
        model: HandleUnion[S3Storage],
        dataset: HandleUnion[S3Storage],
        label: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label or self.label,
            model=model,
            dataset=dataset,
            project_id=project_id,
        )
