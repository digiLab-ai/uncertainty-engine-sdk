from uncertainty_engine_types import Handle, S3Storage

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
        project_id="projectid-789",
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
    assert node.project_id == "projectid-789"


def test_train_model_initialization():
    """Test the initialization of the TrainModel node."""

    # Example values, test with handles and direct objects
    config = ModelConfig()
    inputs = S3Storage(bucket="my-bucket", key="input.csv")
    outputs = Handle(node_name="OutputNode", node_handle="outputs")
    label = "Test Train Model"
    project_id = "projectid-123"

    node = TrainModel(
        config=config,
        inputs=inputs,
        outputs=outputs,
        label=label,
        project_id=project_id,
    )

    assert node.node_name == "TrainModel"
    assert node.config == config
    assert node.inputs == inputs
    assert node.outputs == outputs
    assert node.label == label
    assert node.project_id == project_id


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


def test_recommend_initialization():
    """Test the initialization of the Recommend node."""

    model = Handle(node_name="TrainModelNode", node_handle="model")
    number_of_points = 10
    acquisition_function = "ExpectedImprovement"
    label = "Test Recommend"
    project_id = "projectid-123"

    node = Recommend(
        model=model,
        number_of_points=number_of_points,
        acquisition_function=acquisition_function,
        label=label,
        project_id=project_id,
    )

    assert node.node_name == "Recommend"
    assert node.model == model
    assert node.number_of_points == number_of_points
    assert node.acquisition_function == acquisition_function
    assert node.label == label
    assert node.project_id == project_id
