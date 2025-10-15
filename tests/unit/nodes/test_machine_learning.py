from uncertainty_engine_types import Handle, S3Storage

from uncertainty_engine.nodes.machine_learning import PredictModel


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
