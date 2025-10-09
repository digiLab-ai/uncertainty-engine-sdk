from uncertainty_engine_types import Handle, ResourceID

from uncertainty_engine.nodes.resource_management import (
    Download,
    LoadChatHistory,
    LoadDataset,
    LoadDocument,
    LoadModel,
    Save,
)


def test_loadchathistory_initialization() -> None:
    """Test the initialization of the LoadChatHistory node."""

    # Example values
    project_id = "projectid-123"
    file_id = "fileid-456"
    label = "Test Load Chat History"

    node = LoadChatHistory(
        project_id=project_id,
        file_id=file_id,
        label=label,
    )

    assert node.node_name == "LoadChatHistory"
    assert node.project_id == project_id
    assert node.file_id == ResourceID(id=file_id).model_dump()
    assert node.label == label


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


def test_loaddocument_initialization() -> None:
    """Test the initialization of the LoadDocument node."""

    # Example values
    project_id = "projectid-123"
    file_id = "fileid-456"
    label = "Test Load Document"

    node = LoadDocument(
        project_id=project_id,
        file_id=file_id,
        label=label,
    )

    assert node.node_name == "LoadDocument"
    assert node.project_id == project_id
    assert node.file_id == ResourceID(id=file_id).model_dump()
    assert node.label == label


def test_load_model_initialization() -> None:
    """Test the initialisation of the `LoadModel` node."""
    # Example values
    file_id = "resource-456"
    label = "Test Load Model"
    project_id = "projectid-123"

    node = LoadModel(
        label=label,
        file_id=file_id,
        project_id=project_id,
    )

    assert node.node_name == "LoadModel"
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


def test_download_initialization() -> None:
    """Test the initialization of the `Download` node."""

    # Example values
    file_name = Handle(node_name="LoadDataset", node_handle="dataset")
    label = "Test Download"

    node = Download(
        file=file_name,
        label=label,
    )

    assert node.node_name == "Download"
    assert node.file == file_name
    assert node.label == label
