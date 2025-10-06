from uncertainty_engine_types import ResourceID, Handle

from uncertainty_engine.nodes.resource_management import LoadDataset, Save


def test_loaddataset_initialization() -> None:
    """Test the initialization of the LoadDataset node."""

    # Example values
    project_id = "projectid-123"
    file_id = "fileid-456"
    label = "Test Load Dataset"

    node = LoadDataset(
        project_id=project_id,
        file_id=file_id,
        label=label,
    )

    assert node.node_name == "LoadDataset"
    assert node.project_id == project_id
    assert node.file_id == ResourceID(id=file_id).model_dump()
    assert node.label == label


def test_save_initialization() -> None:
    """Test the initialization of the `Save` node."""

    # Example values
    data = Handle(node_name="LoadDataset", node_handle="dataset")
    file_name = "resource-456"
    label = "Test Save"
    project_id = "projectid-123"

    node = Save(
        label=label,
        data=data,
        file_name=file_name,
        project_id=project_id,
    )

    assert node.node_name == "Save"
    assert node.project_id == project_id
    assert node.file_id == file_name
    assert node.label == label
