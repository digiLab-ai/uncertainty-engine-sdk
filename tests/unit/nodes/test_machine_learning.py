from uncertainty_engine_types import Handle

from uncertainty_engine.nodes.machine_learning import TrainModel


def test_train_model_initialization():
    """Test the initialization of the TrainModel node."""

    # Example handles for config, inputs, and outputs
    config = Handle(node_name="ConfigNode", node_handle="config")
    inputs = Handle(node_name="InputNode", node_handle="inputs")
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
