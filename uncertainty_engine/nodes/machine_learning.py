from typing import Literal, Optional

from typeguard import typechecked
from uncertainty_engine_types import ModelConfig as ModelConfigType
from uncertainty_engine_types import S3Storage

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion


@typechecked
class ModelConfig(Node):
    """
    Config for a machine learning model.

    Args:
        input_variance: Percentage of variance to retain in the input
            data.
        input_retained_dimensions: Number of dimensions to retain in the
            input data.
        output_variance: Percentage of variance to retain in the output
            data.
        output_retained_dimensions: Number of dimensions to retain in
            the output data.
        model_type: Type of model to use.
        kernel: Type of kernel to use for the model.
        warp_inputs: Whether to warp the inputs for the model.
        seed: Seed for reproducible training.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
        project_id: The ID of the project to associate with this node.
    """

    node_name: str = "ModelConfig"
    """The node ID."""

    label: str | None
    """A human-readable label for the node."""

    input_variance: Optional[float] = None
    """Percentage of variance to retain in the input data."""

    input_retained_dimensions: Optional[int] = None
    """Number of dimensions to retain in the input data."""

    output_variance: Optional[float] = None
    """Percentage of variance to retain in the output data."""

    output_retained_dimensions: Optional[int] = None
    """Number of dimensions to retain in the output data."""

    model_type: Optional[
        Literal[
            "BernoulliClassificationGPTorch",
            "SingleTaskGPTorch",
            "SingleTaskVariationalGPTorch",
        ]
    ] = "SingleTaskGPTorch"
    """Type of model to use."""

    kernel: Optional[str] = None
    """Type of kernel to use for the model."""

    warp_inputs: bool = False
    """Whether to warp the inputs for the model."""

    seed: Optional[int] = None
    """Seed for reproducible training."""

    def __init__(
        self,
        input_variance: Optional[float] = None,
        input_retained_dimensions: Optional[int] = None,
        output_variance: Optional[float] = None,
        output_retained_dimensions: Optional[int] = None,
        model_type: Optional[
            Literal[
                "BernoulliClassificationGPTorch",
                "SingleTaskGPTorch",
                "SingleTaskVariationalGPTorch",
            ]
        ] = "SingleTaskGPTorch",
        kernel: Optional[str] = None,
        warp_inputs: bool = False,
        seed: Optional[int] = None,
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            input_variance=input_variance,
            input_retained_dimensions=input_retained_dimensions,
            output_variance=output_variance,
            output_retained_dimensions=output_retained_dimensions,
            model_type=model_type,
            kernel=kernel,
            warp_inputs=warp_inputs,
            seed=seed,
        )


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

    label: str | None
    """A human-readable label for the node."""

    config: HandleUnion[ModelConfigType]
    """A `ModelConfig` for a machine learning model."""

    inputs: HandleUnion[S3Storage]
    """A reference to the input dataset for training the model."""

    outputs: HandleUnion[S3Storage]
    """A reference to the output dataset for training the model."""

    project_id: Optional[str] = None
    """The ID of the project to associate with this node."""

    def __init__(
        self,
        config: HandleUnion[ModelConfigType],
        inputs: HandleUnion[S3Storage],
        outputs: HandleUnion[S3Storage],
        label: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
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

    label: str | None
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
            label=label,
            model=model,
            dataset=dataset,
            project_id=project_id,
        )
