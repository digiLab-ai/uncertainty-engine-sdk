from uncertainty_engine.graph import Graph
from uncertainty_engine.nodes.demo import Add


def test_graph_w_node_instance():
    """
    Test that a node instance can be added to a graph.
    """

    # Define a node
    add = Add(lhs=1, rhs=2)

    # Define a graph
    graph = Graph()

    # Add the node to the graph
    graph.add_node(add, "add1")

    # Verify that the node was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "demo.Add",
                "inputs": {
                    "lhs": ("_", "add1_lhs"),
                    "rhs": ("_", "add1_rhs"),
                },
            }
        }
    }

    # Verify that the external input was logged
    assert graph.external_input == {
        "add1_lhs": 1,
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
                "type": "demo.Add",
                "inputs": {
                    "lhs": ("_", "add1_lhs"),
                    "rhs": ("_", "add1_rhs"),
                },
            },
            "add2": {
                "type": "demo.Add",
                "inputs": {
                    "lhs": ("_", "add2_lhs"),
                    "rhs": ("_", "add2_rhs"),
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
                "type": "demo.Add",
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
    graph.add_edge("_", "add1", "add1_lhs", "lhs")
    graph.add_edge("_", "add1", "add1_rhs", "rhs")

    # Verify that the edge was added to the graph
    assert graph.nodes == {
        "nodes": {
            "add1": {
                "type": "demo.Add",
                "inputs": {
                    "lhs": ("_", "add1_lhs"),
                    "rhs": ("_", "add1_rhs"),
                },
            }
        }
    }


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
                "type": "demo.Add",
                "inputs": {
                    "lhs": ("_", "add1_lhs"),
                    "rhs": ("_", "add1_rhs"),
                },
            },
            "add2": {
                "type": "demo.Add",
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
    graph.add_edge("add1", "add2", "ans", "lhs")

    # Verify that the edge was added to the graph
    assert graph.nodes["nodes"]["add2"]["inputs"]["lhs"] == ("add1", "ans")
