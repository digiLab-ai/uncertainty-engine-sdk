from typing import Any
from unittest.mock import MagicMock, patch

from pytest import raises
from uncertainty_engine_types import NodeInfo, NodeQuery, ToolMetadata

from uncertainty_engine.exceptions import WorkflowValidationError
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.workflow import Workflow
from uncertainty_engine.protocols import Client


def test_workflow_initialization_with_client(
    mock_client: Client,
    workflow_node_graph: dict[str, Any],
    workflow_node_inputs: dict[str, Any],
    node_info_map: dict[str, NodeInfo],
):
    """Test the initialization of the `Workflow` node."""

    def mock_query_nodes(queries: list[NodeQuery]) -> dict[str, NodeInfo]:
        return {
            str(query): node_info_map[f"{query.node_id}@{query.version}"]
            for query in queries
        }

    mock_client.query_nodes = MagicMock(side_effect=mock_query_nodes)

    node = Workflow(
        graph=workflow_node_graph,
        inputs=workflow_node_inputs,
        client=mock_client,
    )

    assert node.node_name == "Workflow"
    assert node.graph == workflow_node_graph
    assert node.inputs == workflow_node_inputs
    assert node.client == mock_client

    # Ensure `query_nodes` was called with a non-empty list of NodeQuery
    assert mock_client.query_nodes.call_count == 1
    call_args, _ = mock_client.query_nodes.call_args
    queries = call_args[0]
    assert isinstance(queries, list)
    assert queries, "Expected at least one NodeQuery to be issued"
    assert all(isinstance(q, NodeQuery) for q in queries)

    # Ensure the workflow populated its nodes list with the expected node infos
    expected_nodes_list = {
        f"{node_data['type']}@{node_data['version']}": node_info_map[
            f"{node_data['type']}@{node_data['version']}"
        ]
        for node_data in workflow_node_graph["nodes"].values()
    }
    assert getattr(node, "nodes_list", None) == expected_nodes_list


def test_workflow_initialization_no_client(simple_graph: Graph):
    """
    Test the initialization of the `Workflow` node when no client is
    passed.
    """
    node = Workflow(
        graph=simple_graph.nodes,
        inputs=simple_graph.external_input,
    )

    assert node.node_name == "Workflow"
    assert node.graph == {
        "nodes": {
            "add": {
                "inputs": {
                    "lhs": {
                        "node_handle": "add_lhs",
                        "node_name": "_",
                    },
                    "rhs": {
                        "node_handle": "add_rhs",
                        "node_name": "_",
                    },
                },
                "type": "Add",
                "version": "0.2.0",
            },
        },
    }
    assert node.inputs == {"add_lhs": 1, "add_rhs": 2}
    assert node.client is None
    assert node.nodes_list is None


def test_validate():
    """Assert validate raises if `self.nodes_list` is unavailable."""
    workflow = Workflow(graph={"nodes": {}}, inputs={})

    with raises(
        ValueError,
        match="Failed to validate workflow. Nodes list is not available.",
    ):
        workflow.validate()


@patch("uncertainty_engine.nodes.workflow.WorkflowValidator")
def test_validate_calls_validator_when_nodes_available(mock_class: MagicMock):
    """Assert validator is called when `self.nodes_list` is available."""
    workflow = Workflow(graph={"nodes": {}}, inputs={})
    workflow.nodes_list = {}
    mock_instance = mock_class.return_value
    mock_instance.validate = MagicMock()

    workflow.validate()

    mock_class.assert_called_once_with(
        node_info_map={},
        graph=workflow.graph,
        inputs=workflow.inputs,
        requested_output=workflow.requested_output,
    )
    mock_instance.validate.assert_called_once()


@patch("uncertainty_engine.nodes.workflow.WorkflowValidator")
def test_validate_happy_path(
    mock_class: MagicMock,
    mock_client_query_nodes_success: MagicMock,
    workflow_node_graph: dict[str, Any],
    workflow_node_inputs: dict[str, Any],
):
    """Assert validate delegates to WorkflowValidator when node infos are fetched."""
    workflow = Workflow(
        graph=workflow_node_graph,
        inputs=workflow_node_inputs,
        client=mock_client_query_nodes_success,
    )
    mock_instance = mock_class.return_value
    mock_instance.validate = MagicMock()
    mock_class.reset_mock()
    mock_instance.validate.reset_mock()

    workflow.validate()

    assert workflow.nodes_list is not None
    mock_class.assert_called_once_with(
        node_info_map=workflow.nodes_list,
        graph=workflow.graph,
        inputs=workflow.inputs,
        requested_output=workflow.requested_output,
    )
    mock_instance.validate.assert_called_once()


def test_get_nodes_list_returns_none_on_query_error(
    mock_client: Client,
    workflow_node_graph: dict[str, Any],
):
    """Assert node list fetch fails fast when `query_nodes` raises an error."""
    mock_client.query_nodes = MagicMock(side_effect=Exception("query failed"))
    workflow = Workflow(graph=workflow_node_graph, inputs={})

    nodes_list = workflow._get_nodes_list(mock_client)

    assert nodes_list is None


def test_init_raises_query_error_context(
    mock_client: Client,
    workflow_node_graph: dict[str, Any],
):
    """Assert init includes query failure context when node lookup fails."""
    mock_client.query_nodes = MagicMock(side_effect=Exception("unknown node version"))

    with raises(
        WorkflowValidationError,
        match=("Failed to validate workflow. Error: unknown node version"),
    ):
        Workflow(graph=workflow_node_graph, inputs={}, client=mock_client)


def test_workflow_tool_metadata_validate_complete_called():
    """Assert validate_complete is called when tool_metadata is provided."""
    mock_tool_metadata = MagicMock(spec=ToolMetadata)
    mock_tool_metadata.is_empty.return_value = False
    mock_tool_metadata.validate_complete = MagicMock()

    Workflow(
        graph={"nodes": {}},
        inputs={},
        tool_metadata=mock_tool_metadata,
    )

    mock_tool_metadata.validate_complete.assert_called_once()


def test_workflow_tool_metadata_set_to_none_when_empty():
    """Assert tool_metadata is set to None when is_empty() returns True."""
    mock_tool_metadata = MagicMock(spec=ToolMetadata)
    mock_tool_metadata.is_empty.return_value = True
    mock_tool_metadata.validate_complete = MagicMock()

    workflow = Workflow(
        graph={"nodes": {}},
        inputs={},
        tool_metadata=mock_tool_metadata,
    )

    # Check that validate_complete was called
    mock_tool_metadata.validate_complete.assert_called_once()
    # Check that tool_metadata was set to None
    assert workflow.tool_metadata is None


def test_workflow_tool_metadata_preserved_when_complete():
    """Assert tool_metadata is preserved when complete and not empty."""
    mock_tool_metadata = MagicMock(spec=ToolMetadata)
    mock_tool_metadata.is_empty.return_value = False
    mock_tool_metadata.validate_complete = MagicMock()

    workflow = Workflow(
        graph={"nodes": {}},
        inputs={},
        tool_metadata=mock_tool_metadata,
    )

    mock_tool_metadata.validate_complete.assert_called_once()
    assert workflow.tool_metadata == mock_tool_metadata


def test_workflow_tool_metadata_incomplete_raises_error():
    """Assert ValueError is raised when tool_metadata is incomplete."""
    mock_tool_metadata = MagicMock(spec=ToolMetadata)
    mock_tool_metadata.validate_complete = MagicMock(
        side_effect=ValueError("ToolMetadata must have both inputs and outputs")
    )

    with raises(ValueError, match="ToolMetadata must have both inputs and outputs"):
        Workflow(
            graph={"nodes": {}},
            inputs={},
            tool_metadata=mock_tool_metadata,
        )


def test_workflow_tool_metadata_none_by_default():
    """Assert tool_metadata is None when not provided."""
    workflow = Workflow(
        graph={"nodes": {}},
        inputs={},
    )

    assert workflow.tool_metadata is None


def test_from_graph_validate_tool_metadata_called():
    """Assert validate_tool_metadata is called on the graph object."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.nodes = {"nodes": {}}
    mock_graph.external_input = {}
    mock_graph.external_input_id = "_"
    mock_graph.tool_metadata = MagicMock(spec=ToolMetadata)
    mock_graph.tool_metadata.is_empty.return_value = True
    mock_graph.validate_tool_metadata = MagicMock()

    Workflow.from_graph(mock_graph)

    mock_graph.validate_tool_metadata.assert_called_once()


def test_from_graph_tool_metadata_none_when_empty():
    """Assert tool_metadata is set to None when graph's tool_metadata is empty."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.nodes = {"nodes": {}}
    mock_graph.external_input = {}
    mock_graph.external_input_id = "_"
    mock_graph.tool_metadata = MagicMock(spec=ToolMetadata)
    mock_graph.tool_metadata.is_empty.return_value = True
    mock_graph.validate_tool_metadata = MagicMock()

    workflow = Workflow.from_graph(mock_graph)

    assert workflow.tool_metadata is None


def test_from_graph_tool_metadata_preserved_when_not_empty():
    """Assert tool_metadata is passed through when not empty."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.nodes = {"nodes": {}}
    mock_graph.external_input = {}
    mock_graph.external_input_id = "_"
    mock_tool_metadata = MagicMock(spec=ToolMetadata)
    mock_tool_metadata.is_empty.return_value = False
    mock_graph.tool_metadata = mock_tool_metadata
    mock_graph.validate_tool_metadata = MagicMock()

    workflow = Workflow.from_graph(mock_graph)

    assert workflow.tool_metadata == mock_tool_metadata


def test_from_graph_raises_error_when_validation_fails():
    """Assert ValueError is raised when validate_tool_metadata fails."""
    mock_graph = MagicMock(spec=Graph)
    mock_graph.nodes = {"nodes": {}}
    mock_graph.external_input = {}
    mock_graph.validate_tool_metadata = MagicMock(
        side_effect=ValueError("Tool metadata validation failed")
    )

    with raises(ValueError, match="Tool metadata validation failed"):
        Workflow.from_graph(mock_graph)
