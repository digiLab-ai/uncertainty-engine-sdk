from uncertainty_engine_types import Handle, ModelConfig, S3Storage

from uncertainty_engine.nodes.machine_learning import PredictModel, TrainModel


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
