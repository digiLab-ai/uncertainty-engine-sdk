from unittest.mock import patch

from uncertainty_engine.graph import Graph
from uncertainty_engine.visualization import visualize_graph


def test_visualize_graph_show(simple_graph: Graph):
    """
    Verify that the visualize_graph function displays the graph when no filename is provided.

    Args:
        simple_graph: A simple graph with a single node.
    """
    with patch("uncertainty_engine.visualization.plt.show") as mock_show:
        visualize_graph(simple_graph)

        mock_show.assert_called_once()


def test_visualize_graph_save(simple_graph: Graph):
    """
    Verify that the visualize_graph function saves the graph when a filename is provided.

    Args:
        simple_graph: A simple graph with a single node.
    """
    with patch("uncertainty_engine.visualization.plt.savefig") as mock_savefig:
        visualize_graph(simple_graph, "test.png")

        mock_savefig.assert_called_once_with("test.png")
