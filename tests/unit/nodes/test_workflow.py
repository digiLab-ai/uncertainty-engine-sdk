from uncertainty_engine.client import Client
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.workflow import Workflow


def test_workflow_initialization(mock_client: Client, simple_graph: Graph):
    """Test the initialization of the `Workflow` node."""
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
    assert node.inputs == {'add_lhs': 1, 'add_rhs': 2}
    assert node.client == mock_client
