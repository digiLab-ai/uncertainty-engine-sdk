import pytest
from uncertainty_engine_types import Handle, NodeInputInfo, NodeOutputInfo

from uncertainty_engine.exceptions import GraphValidationError
from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.base import Node
from uncertainty_engine.nodes.basic import Add


@pytest.mark.parametrize(
    "node_instance,node_label",
    [
        (Add(lhs=1, rhs=2), "add1"),
        (Add(lhs=1, rhs=2, label="add1"), None),
        (Add(lhs=1, rhs=2, label="ADD1"), "add1"),
    ],
)
def test_graph_w_node_instance(node_instance, node_label):
    """
    Test that a node instance can be added to a graph.

    Args:
        node_instance: The node instance to add.
        node_label: The label passed to add_node.
    """

    # Define a graph
    graph = Graph()

    # Add the node to the graph
    graph.add_node(node_instance, node_label)

    # Verify that the node was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add1_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            }
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
        "add1_rhs": 2,
    }


def test_graph_w_node_instance_no_label():
    """
    Verify that error is raised if node instance has no label and no label is passed.
    """

    # Define a node
    add = Add(lhs=1, rhs=2)

    # Define a graph
    graph = Graph()

    with pytest.raises(ValueError):
        graph.add_node(add)


def test_graph_w_node_instance_handle():
    """
    Test that a node instance with a handle can be added to a graph.
    """

    # Define a node
    add = Add(lhs=Handle("a.b"), rhs=2, label="add1")

    # Define a graph
    graph = Graph()

    # Add the node to the graph
    graph.add_node(add)

    # Verify that the node was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "a", "node_handle": "b"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            }
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_rhs": 2,
    }


def test_graph_w_node_multiple():
    """
    Test that multiple nodes can be added to a graph.
    """

    # Define nodes
    add1 = Add(lhs=1, rhs=2)
    add2 = Add(lhs=3, rhs=4)

    # Define a graph
    graph = Graph()

    # Add the nodes to the graph
    graph.add_node(add1, "add1")
    graph.add_node(add2, "add2")

    # Verify that the nodes were added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add1_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            },
            "add2": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add2_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add2_rhs"},
                },
            },
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
        "add1_rhs": 2,
        "add2_lhs": 3,
        "add2_rhs": 4,
    }


def test_graph_w_node_multiple_from_list():
    """
    Test that multiple nodes can be added to a graph from a list.
    """
    nodes = [
        Add(lhs=1, rhs=2, label="add1"),
        Add(lhs=3, rhs=4, label="add2"),
    ]

    # Define a graph
    graph = Graph()

    # Add the nodes to the graph
    graph.add_nodes_from(nodes)

    # Verify that the nodes were added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add1_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            },
            "add2": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add2_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add2_rhs"},
                },
            },
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
        "add1_rhs": 2,
        "add2_lhs": 3,
        "add2_rhs": 4,
    }


def test_graph_w_node_class():
    """
    Test that a node class can be added to a graph.
    """

    # Define a graph
    graph = Graph()

    # Add the node to the graph
    graph.add_node(Add, "add1")

    # Verify that the node was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": None,
                    "rhs": None,
                },
            }
        }
    }

    # Add external inputs
    graph.add_input("add1_lhs", 1)
    graph.add_input("add1_rhs", 2)

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
        "add1_rhs": 2,
    }

    # Add an edge between the inputs and the node
    graph.add_edge("_", "add1_lhs", "add1", "lhs")
    graph.add_edge("_", "add1_rhs", "add1", "rhs")

    # Verify that the edge was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add1_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            }
        }
    }


def test_graph_w_node_class_no_label():
    """
    Verify that error is raised if node class is added and no label is passed.
    """

    # Define a graph
    graph = Graph()

    with pytest.raises(ValueError):
        graph.add_node(Add)


def test_graph_connect_nodes():
    """
    Test that nodes can be connected with edges in a graph.
    """

    # Define a node
    add = Add(lhs=1, rhs=2)

    # Define a graph
    graph = Graph()

    # Add the node to the graph
    graph.add_node(add, "add1")

    # Add another node to the graph
    graph.add_node(Add, "add2")

    # Verify that the nodes were added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "Add",
                "inputs": {
                    "lhs": {"node_name": "_", "node_handle": "add1_lhs"},
                    "rhs": {"node_name": "_", "node_handle": "add1_rhs"},
                },
            },
            "add2": {
                "type": "Add",
                "inputs": {
                    "lhs": None,
                    "rhs": None,
                },
            },
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
        "add1_rhs": 2,
    }

    # Add an edge between the two nodes
    graph.add_edge("add1", "ans", "add2", "lhs")

    # Verify that the edge was added to the graph
    assert graph.nodes["nodes"]["add2"]["inputs"]["lhs"] == {
        "node_name": "add1",
        "node_handle": "ans",
    }


def test_process_metadata_with_tool_inputs():
    """
    Test that _process_metadata correctly processes tool inputs from a node.
    """
    # Define a node with tool metadata
    node = Node("test_node", label="test_label")
    node_input_info = NodeInputInfo(
        type="int", label="Input 1", description="Description for input 1"
    )
    node.tool_metadata.inputs["test_label"] = {"input1": node_input_info}

    # Define a graph
    graph = Graph()

    # Process metadata
    graph.add_node(node)

    # Verify that tool inputs were added to the graph's metadata
    assert "test_label" in graph.tool_metadata.inputs
    assert "input1" in graph.tool_metadata.inputs["test_label"]
    assert graph.tool_metadata.inputs["test_label"]["input1"] == node_input_info


def test_process_metadata_with_tool_outputs():
    """
    Test that _process_metadata correctly processes tool outputs from a node.
    """
    # Define a node with tool metadata
    node = Node("test_node", label="test_label")
    node_output_info = NodeOutputInfo(
        type="float", label="Output 1", description="Description for output 1"
    )
    node.tool_metadata.outputs["test_label"] = {"output1": node_output_info}

    # Define a graph
    graph = Graph()

    # Process metadata
    graph.add_node(node)

    # Verify that tool outputs were added to the graph's metadata
    assert "test_label" in graph.tool_metadata.outputs
    assert "output1" in graph.tool_metadata.outputs["test_label"]
    assert graph.tool_metadata.outputs["test_label"]["output1"] == node_output_info


def test_process_metadata_with_no_tool_metadata():
    """
    Test that _process_metadata does nothing if the node has no tool metadata.
    """
    # Define a node without tool metadata
    node = Node("test_node", label="test_label")

    # Define a graph
    graph = Graph()

    # Process metadata
    graph.add_node(node)

    # Verify that tool metadata remains empty
    assert graph.tool_metadata.inputs == {}
    assert graph.tool_metadata.outputs == {}


def test_graph_add_node_duplicate_label_raises_error():
    """
    Verify that an exception is raised if a node with a duplicate label
    is added.
    """
    graph = Graph(prevent_node_overwrite=True)

    node1 = Add(lhs=1, rhs=2, label="duplicate")
    node2 = Node("test_node", label="duplicate", arg1=5)

    graph.add_node(node1)

    with pytest.raises(
        GraphValidationError,
        match="Label 'duplicate' already used in the graph",
    ):
        graph.add_node(node2)

    # Verify that only the first node is in the graph
    assert graph.nodes["nodes"] == {
        "duplicate": {
            "type": "Add",
            "inputs": {
                "lhs": {"node_name": "_", "node_handle": "duplicate_lhs"},
                "rhs": {"node_name": "_", "node_handle": "duplicate_rhs"},
            },
        }
    }

    # Verify that the external input was logged for the first node
    assert graph.external_input == {
        "duplicate_lhs": 1,
        "duplicate_rhs": 2,
    }


def test_graph_add_node_duplicate_label_allowed():
    """
    Verify that no exception is raised if a node with a duplicate label
    is added when prevent_node_overwrite is False.
    """
    graph = Graph(prevent_node_overwrite=False)

    add1 = Add(lhs=1, rhs=2, label="duplicate")
    add2 = Add(lhs=3, rhs=4, label="duplicate")

    graph.add_node(add1)
    graph.add_node(add2)

    # Verify that the second node overwrote the first
    assert graph.nodes["nodes"]["duplicate"]["inputs"] == {
        "lhs": {"node_name": "_", "node_handle": "duplicate_lhs"},
        "rhs": {"node_name": "_", "node_handle": "duplicate_rhs"},
    }

    # Verify that the external input was logged for the second node
    assert graph.external_input == {
        "duplicate_lhs": 3,
        "duplicate_rhs": 4,
    }


def test_graph_add_node_duplicate_label_warning():
    """
    Verify that a warning is issued when prevent_node_overwrite is None
    (default).
    """
    with pytest.warns(
        FutureWarning,
        match="The default value of `prevent_node_overwrite` will"
        " change to `True` in a future release. Please set this "
        "argument explicitly to `False` to maintain the ability to"
        " overwrite nodes.",
    ):
        Graph()
