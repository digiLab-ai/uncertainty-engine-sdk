from uncertainty_engine_types import Handle
from uncertainty_engine_types import ModelConfig as ModelConfigType

from uncertainty_engine.client import Client
from uncertainty_engine.nodes.machine_learning import (
    ExportTorchScript,
    ModelConfig,
    PredictModel,
    PredictPosteriorConditioning,
    Recommend,
    ScoreModel,
    TrainModel,
)


def test_export_torch_script_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the ExportTorchScript node."""

    label = "Test Export Torch Script"

    node = ExportTorchScript(
        model=mock_handle,
        validation_inputs=mock_handle,
        label=label,
        client=mock_client,
    )

    assert node.node_name == "ExportTorchScript"
    assert node.model == mock_handle
    assert node.validation_inputs == mock_handle
    assert node.observation_noise is True
    assert node.label == label
    assert node.client == mock_client


def test_model_config_initialization(mock_client: Client):
    """Test the initialization of the ModelConfig node."""

    node = ModelConfig(
        input_variance=0.95,
        input_retained_dimensions=5,
        output_variance=0.9,
        output_retained_dimensions=3,
        model_type="SingleTaskVariationalGPTorch",
        kernel="RBF",
        warp_inputs=True,
        seed=42,
        label="Model Config",
        client=mock_client,
    )

    assert node.node_name == "ModelConfig"
    assert node.input_variance == 0.95
    assert node.input_retained_dimensions == 5
    assert node.output_variance == 0.9
    assert node.output_retained_dimensions == 3
    assert node.model_type == "SingleTaskVariationalGPTorch"
    assert node.kernel == "RBF"
    assert node.warp_inputs is True
    assert node.seed == 42
    assert node.label == "Model Config"
    assert node.client == mock_client


def test_predict_model_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the PredictModel node."""

    # Example values, test with handles and direct objects
    label = "Test Predict Model"

    node = PredictModel(
        model=mock_handle,
        dataset=mock_handle,
        label=label,
        client=mock_client,
    )

    assert node.node_name == "PredictModel"
    assert node.model == mock_handle
    assert node.dataset == mock_handle
    assert node.label == label
    assert node.client == mock_client


def test_predict_posterior_conditioning_initialization(
    mock_client: Client, mock_handle: Handle
):
    """Test the initialization of the PredictPosteriorConditioning node."""

    node = PredictPosteriorConditioning(
        conditioning_inputs=mock_handle,
        conditioning_outputs=mock_handle,
        model=mock_handle,
        prediction_inputs=mock_handle,
        client=mock_client,
    )

    assert node.node_name == "PredictPosteriorConditioning"
    assert node.conditioning_inputs == mock_handle
    assert node.conditioning_outputs == mock_handle
    assert node.model == mock_handle
    assert node.prediction_inputs == mock_handle
    assert node.client == mock_client


def test_recommend_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the Recommend node."""

    num_of_points = 10
    acquisition_function = "ExpectedImprovement"

    node = Recommend(
        model=mock_handle,
        acquisition_function=acquisition_function,
        num_of_points=num_of_points,
        client=mock_client,
    )

    assert node.node_name == "Recommend"
    assert node.model == mock_handle
    assert node.acquisition_function == acquisition_function
    assert node.num_of_points == num_of_points
    assert node.client == mock_client


def test_train_model_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the TrainModel node."""

    # Example values, test with handles and direct objects
    config = ModelConfigType()
    label = "Test Train Model"

    node = TrainModel(
        config=config,
        inputs=mock_handle,
        outputs=mock_handle,
        label=label,
        client=mock_client,
    )

    assert node.node_name == "TrainModel"
    assert node.config == config
    assert node.inputs == mock_handle
    assert node.outputs == mock_handle
    assert node.label == label
    assert node.client == mock_client


def test_score_model_initialization(mock_client: Client, mock_handle: Handle):
    """Test the initialization of the ScoreModel node."""

    label = "Test Score Model"

    node = ScoreModel(
        predictions=mock_handle,
        truth=mock_handle,
        label=label,
        client=mock_client,
    )

    assert node.node_name == "ScoreModel"
    assert node.predictions == mock_handle
    assert node.truth == mock_handle
    assert node.predictions_uncertainty is None
    assert node.train_outputs is None
    assert node.metrics == ["MSE", "RMSE", "R2"]
    assert node.label == label
    assert node.client == mock_client
