from uncertainty_engine_types import ResourceID

from uncertainty_engine.nodes.resource_management import LoadDataset


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
