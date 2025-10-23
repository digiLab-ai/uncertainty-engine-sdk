from typing import Literal, Optional

from typeguard import typechecked
from uncertainty_engine_types import ModelConfig as ModelConfigType
from uncertainty_engine_types import S3Storage

from uncertainty_engine.nodes.base import Node
from uncertainty_engine.utils import HandleUnion

AvailableAcquisitions = Literal[
    "ExpectedImprovement",
    "LogExpectedImprovement",
    "PosteriorMean",
    "PosteriorStandardDeviation",
    "MonteCarloExpectedImprovement",
    "MonteCarloLogExpectedImprovement",
    "MonteCarloNegativeIntegratedPosteriorVariance",
]

AvailableScoreMetrics = Literal[
    "MSE",
    "RMSE",
    "R2",
    "MSLL",
]


@typechecked
class ExportTorchScript(Node):
    """
    Export to a TorchScript file so you can download your optimised
    model.

    Args:
        model: The model to export to TorchScript.
        validation_inputs: Sample input data to validate the exported
            model's predictions.
        observation_noise: Whether to include observation noise.
            Defaults to `False`.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
    """

    node_name: str = "ExportTorchScript"
    """The node ID."""

    model: HandleUnion[S3Storage]
    """The model to export to TorchScript."""

    validation_inputs: HandleUnion[S3Storage]
    """
    Sample input data to validate the exported model's predictions.
    """

    observation_noise: bool
    """Whether to include observation noise."""

    label: str | None
    """A human-readable label for the node."""

    def __init__(
        self,
        model: HandleUnion[S3Storage],
        validation_inputs: HandleUnion[S3Storage],
        observation_noise: bool = True,
        label: str | None = None,
    ):
        super().__init__(
            node_name=self.node_name,
            model=model,
            validation_inputs=validation_inputs,
            observation_noise=observation_noise,
            label=label,
        )


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

    def __init__(
        self,
        model: HandleUnion[S3Storage],
        dataset: HandleUnion[S3Storage],
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            model=model,
            dataset=dataset,
        )


@typechecked
class PredictPosteriorConditioning(Node):
    """
    Make predictions with a trained Gaussian process model whilst
    incorporating information from new data with posterior conditioning.

    Args:
        conditioning_inputs: A reference to the input dataset for
            conditioning.
        conditioning_outputs: A reference to the output dataset for
            conditioning.
        model: A reference to the trained machine-learning model to use
            for prediction.
        prediction_inputs: A reference to the input dataset for making
            predictions.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
    """

    conditioning_inputs: HandleUnion[S3Storage]
    """A reference to the input dataset for conditioning."""

    conditioning_outputs: HandleUnion[S3Storage]
    """A reference to the output dataset for conditioning."""

    model: HandleUnion[S3Storage]
    """
    A reference to the trained machine-learning model to use for
    prediction.
    """

    prediction_inputs: HandleUnion[S3Storage]
    """A reference to the input dataset for making predictions."""

    label: str | None
    """A human-readable label for the node."""

    node_name: str = "PredictPosteriorConditioning"
    """The node ID."""

    def __init__(
        self,
        conditioning_inputs: HandleUnion[S3Storage],
        conditioning_outputs: HandleUnion[S3Storage],
        model: HandleUnion[S3Storage],
        prediction_inputs: HandleUnion[S3Storage],
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            conditioning_inputs=conditioning_inputs,
            conditioning_outputs=conditioning_outputs,
            model=model,
            prediction_inputs=prediction_inputs,
        )


@typechecked
class Recommend(Node):
    """
    Draw recommended data points from a trained model.

    Args:
        acquisition_function: The acquisition function to use for
            recommending points.
        model: A reference to the trained machine-learning model to use
            for recommendation.
        num_of_points: The number of points to recommend.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
    """

    acquisition_function: AvailableAcquisitions
    """The acquisition function to use for recommending points."""

    model: HandleUnion[S3Storage]
    """
    A reference to the trained machine-learning model to use for
    recommendation.
    """

    node_name: str = "Recommend"
    """The node ID."""

    num_of_points: int
    """The number of points to recommend."""

    label: str | None
    """A human-readable label for the node."""

    def __init__(
        self,
        acquisition_function: AvailableAcquisitions,
        model: HandleUnion[S3Storage],
        num_of_points: int,
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            acquisition_function=acquisition_function,
            model=model,
            num_of_points=num_of_points,
            label=label,
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

    def __init__(
        self,
        config: HandleUnion[ModelConfigType],
        inputs: HandleUnion[S3Storage],
        outputs: HandleUnion[S3Storage],
        label: Optional[str] = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            config=config,
            inputs=inputs,
            outputs=outputs,
        )


@typechecked
class ScoreModel(Node):
    """
    Score a machine-learning model using your specified metrics.

    Args:
        predictions: Dataset containing predicted values for scoring the
            model.
        truth: Dataset containing actual values for scoring the model.
        predictions_uncertainty: Standard deviation of predicted output
            data. Only required for MSLL metric.
        train_outputs: Target output data used for training. Only
            required for MSLL metric.
        metrics: A list of metrics to be used when scoring the model.
            Will default to MSE, RMSE and R2.
        label: A human-readable label for the node. This should be
            unique to all other node labels in a workflow.
    """

    node_name: str = "ScoreModel"
    """The node ID."""

    label: str | None
    """A human-readable label for the node."""

    predictions: HandleUnion[S3Storage]
    """Dataset containing predicted values for scoring the model."""

    truth: HandleUnion[S3Storage]
    """Dataset containing actual values for scoring the model."""

    predictions_uncertainty: HandleUnion[S3Storage] | None
    """
    Standard deviation of predicted output data. Only required for MSLL
    metric.
    """

    train_outputs: HandleUnion[S3Storage] | None
    """
    Target output data used for training. Only required for MSLL metric.
    """

    metrics: list[AvailableScoreMetrics]
    """
    A list of metrics to be used when scoring the model.
    """

    def __init__(
        self,
        predictions: HandleUnion[S3Storage],
        truth: HandleUnion[S3Storage],
        predictions_uncertainty: HandleUnion[S3Storage] | None = None,
        train_outputs: HandleUnion[S3Storage] | None = None,
        metrics: list[AvailableScoreMetrics] = ["MSE", "RMSE", "R2"],
        label: str | None = None,
    ):
        super().__init__(
            node_name=self.node_name,
            label=label,
            predictions=predictions,
            truth=truth,
            predictions_uncertainty=predictions_uncertainty,
            train_outputs=train_outputs,
            metrics=metrics,
        )
