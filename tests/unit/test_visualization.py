import pytest

# Skip if the `vis` dependencies are not installed
pytest.importorskip("matplotlib")
pytest.importorskip("networkx")

from networkx import MultiDiGraph

import uncertainty_engine.visualization as vis
from uncertainty_engine.graph import Graph


class TestHelper:
    def test_to_networkx(self, simple_graph: Graph, simple_node_label: str):
        """
        Verify that a Graph can be converted to a NetworkX graph.

        Args:
            simple_graph: A simple graph with a single node.
            simple_node_label: The label of the single node in the graph.
        """
        # Convert the graph to a NetworkX graph
        nx_graph = vis._to_networkx(simple_graph)

        # Verify that the graph is a MultiDiGraph
        assert isinstance(nx_graph, MultiDiGraph)

        # Verify that the graph has two nodes.
        # One for the user input and one for the Add node.
        assert len(nx_graph.nodes) == 2

        # Verify that the user input node has the correct label
        assert nx_graph.nodes[simple_graph.external_input_id]["label"] == "User Input"

        # Verify that the Add node has the correct label
        assert nx_graph.nodes[simple_node_label]["label"] == "add"

        # Verify the edge between the user input and the Add node
        assert nx_graph.has_edge(simple_graph.external_input_id, simple_node_label)
        assert (
            nx_graph.edges[simple_graph.external_input_id, simple_node_label, 0][
                "label"
            ]
            == "lhs"
        )
        assert (
            nx_graph.edges[simple_graph.external_input_id, simple_node_label, 1][
                "label"
            ]
            == "rhs"
        )

        # Add the NetworkX graph to the TestHelper class for use in other tests
        TestHelper.nx_graph = nx_graph

    def test_get_node_sizes(self, simple_graph: Graph, simple_node_label: str):
        """
        Verify that the node sizes are correctly calculated.

        Args:
            simple_graph: A simple graph with a single node.
            simple_node_label: The label of the single node in the graph.
        """
        # Define the node sizes
        node_sizes = vis._get_node_sizes(TestHelper.nx_graph)

        # Verify all sizes are bigger than the minimum size
        assert all([size >= vis.MINIMUM_NODE_SIZE for size in node_sizes.values()])

        # Verify the size of the user input node is greater than the add node
        assert (
            node_sizes[simple_graph.external_input_id] > node_sizes[simple_node_label]
        )

    def test_get_connection_style(self):
        """
        Verify that the connection style is correctly calculated.
        """
        # Define a connection style
        connection_style = vis._get_connection_style(TestHelper.nx_graph)

        # Verify that the first element is a straight line
        assert connection_style[0] == "arc3,rad=0"

        # Verify that the second element is an arc
        assert connection_style[1] == f"arc3,rad={vis.MINIMUM_CONNECTION_ARC}"

    def test_get_node_positions(self):
        """
        Verify that the node positions are correctly calculated.
        """
        # Calculate the node positions
        pos = vis._get_node_positions(TestHelper.nx_graph)

        # Verify all nodes have a position
        assert list(pos.keys()) == list(TestHelper.nx_graph.nodes)
        assert all(len(p) == 2 for p in pos.values())
