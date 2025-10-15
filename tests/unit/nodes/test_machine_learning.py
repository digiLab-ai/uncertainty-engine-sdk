from typing import Optional

from typeguard import typechecked
from uncertainty_engine_types import Handle, ModelConfig, S3Storage

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.nodes.machine_learning import PredictModel
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


def test_predict_model_initialization():
    """Test the initialization of the PredictModel node."""

    # Example values, test with handles and direct objects
    model = Handle(node_name="TrainModelNode", node_handle="model")
    dataset = S3Storage(bucket="my-bucket", key="predict_input.csv")
    label = "Test Predict Model"
    project_id = "projectid-456"

    node = PredictModel(
        model=model,
        dataset=dataset,
        label=label,
        project_id=project_id,
    )

    assert node.node_name == "PredictModel"
    assert node.model == model
    assert node.dataset == dataset
    assert node.label == label
    assert node.project_id == project_id
