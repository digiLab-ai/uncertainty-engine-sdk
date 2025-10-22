from uncertainty_engine_types import Handle
from uncertainty_engine_types import ModelConfig as ModelConfigType
from uncertainty_engine_types import S3Storage

from uncertainty_engine.nodes.machine_learning import (
    ModelConfig,
    PredictModel,
    Recommend,
    TrainModel,
)


def test_model_config_initialization():
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


def test_predict_model_initialization():
    """Test the initialization of the PredictModel node."""

    # Example values, test with handles and direct objects
    # TODO: Use a fixture for common test values
    model = Handle(node_name="TrainModelNode", node_handle="model")
    dataset = S3Storage(bucket="my-bucket", key="predict_input.csv")
    label = "Test Predict Model"

    node = PredictModel(
        model=model,
        dataset=dataset,
        label=label,
    )

    assert node.node_name == "PredictModel"
    assert node.model == model
    assert node.dataset == dataset
    assert node.label == label


def test_recommend_initialization():
    """Test the initialization of the Recommend node."""

    num_of_points = 10
    acquisition_function = "ExpectedImprovement"
    # TODO: Use a fixture for common test values
    model = Handle(node_name="TrainModelNode", node_handle="model")

    node = Recommend(
        model=model,
        acquisition_function=acquisition_function,
        num_of_points=num_of_points,
    )

    assert node.node_name == "Recommend"
    assert node.model == model
    assert node.acquisition_function == acquisition_function
    assert node.num_of_points == num_of_points


def test_train_model_initialization():
    """Test the initialization of the TrainModel node."""

    # Example values, test with handles and direct objects
    config = ModelConfigType()
    # TODO: Use a fixture for common test values
    inputs = S3Storage(bucket="my-bucket", key="input.csv")
    outputs = Handle(node_name="OutputNode", node_handle="outputs")
    label = "Test Train Model"

    node = TrainModel(
        config=config,
        inputs=inputs,
        outputs=outputs,
        label=label,
    )

    assert node.node_name == "TrainModel"
    assert node.config == config
    assert node.inputs == inputs
    assert node.outputs == outputs
    assert node.label == label
