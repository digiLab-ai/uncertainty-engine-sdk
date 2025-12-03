from typing import Any

from unittest.mock import MagicMock, patch
from warnings import catch_warnings

from pytest import raises
from uncertainty_engine_types import NodeInfo

from uncertainty_engine.client import Client
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.workflow import Workflow


def test_workflow_initialization_with_client(
    mock_client: Client,
    workflow_node_graph: dict[str, Any],
    workflow_node_inputs: dict[str, Any],
    node_info_list: list[NodeInfo],
):
    """Test the initialization of the `Workflow` node."""
    mock_client.list_nodes = MagicMock(
        return_value=[ni.model_dump() for ni in node_info_list]
    )

    node = Workflow(
        graph=workflow_node_graph,
        inputs=workflow_node_inputs,
        client=mock_client,
    )

    assert node.node_name == "Workflow"
    assert node.graph == workflow_node_graph
    assert node.inputs == workflow_node_inputs
    assert node.client == mock_client
    assert node.nodes_list == node_info_list


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
            },
        },
    }
    assert node.inputs == {"add_lhs": 1, "add_rhs": 2}
    assert node.client is None
    assert node.nodes_list is None


def test_get_nodes_list(mock_client: Client, add_node_info: NodeInfo):
    """Assert a list of NodeInfo is returned."""
    mock_client.list_nodes = MagicMock(return_value=[add_node_info.model_dump()])

    workflow = Workflow(graph={}, inputs={})
    nodes_list = workflow._get_nodes_list(mock_client)

    assert nodes_list == [add_node_info]


def test_get_nodes_list_returns_none_on_error(mock_client: Client):
    """Assert raises valid warning if unable to get nodes list."""
    mock_client.list_nodes = MagicMock(side_effect=Exception())
    workflow = Workflow(graph={}, inputs={})

    with catch_warnings(record=True) as w:
        nodes_list = workflow._get_nodes_list(mock_client)

    assert nodes_list is None
    assert len(w) == 1
    assert (
        str(w[0].message)
        == "Unable to get node info list. Workflow node will not be able to perform validation."
    )


def test_validate():
    """Assert validator is called if `self.nodes_list` is available."""
    workflow = Workflow(graph={"nodes": {}}, inputs={})
    workflow.nodes_list = []

    with patch("uncertainty_engine.nodes.workflow.WorkflowValidator") as mock_class:
        mock_instance = mock_class.return_value
        mock_instance.validate = MagicMock()

        workflow.validate()

        mock_instance.validate.assert_called_once()


def test_validate_value_error():
    """Assert `ValueError` is raised if `self.nodes_list` is `None`."""
    workflow = Workflow(graph={}, inputs={})
    workflow.nodes_list = None

    with raises(ValueError, match="Nodes list is not available for validation."):
        workflow.validate()
