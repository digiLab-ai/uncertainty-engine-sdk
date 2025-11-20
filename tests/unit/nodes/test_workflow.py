from unittest.mock import MagicMock

from uncertainty_engine_types import NodeInfo

from uncertainty_engine.client import Client
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.workflow import Workflow


def test_workflow_initialization_with_client(
    mock_client: Client, simple_graph: Graph, add_node_info: NodeInfo
):
    """Test the initialization of the `Workflow` node."""
    mock_client.list_nodes = MagicMock(return_value=[add_node_info.model_dump()])

    node = Workflow(
        graph=simple_graph.nodes,
        inputs=simple_graph.external_input,
        client=mock_client,
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
    assert node.client == mock_client
    assert node.nodes_list == [add_node_info]


def test_workflow_initialization_no_client(simple_graph: Graph):
    """Test the initialization of the `Workflow` node."""
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
    assert node.client == None
    assert node.nodes_list == None
