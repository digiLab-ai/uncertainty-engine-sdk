import itertools as it
from typing import Optional

from typeguard import typechecked

from uncertainty_engine.graph import Graph

try:
    import matplotlib.pyplot as plt
    import networkx as nx
except ImportError:
    raise ImportError(
        "Visualization dependencies not found. Please install with `vis` extra."
    )


MINIMUM_NODE_SIZE = 1000
NODE_SIZE_SCALE = 400
MINIMUM_CONNECTION_ARC = 0.15
AXIS_BUFFER = 0.5


@typechecked
def visualize_graph(graph: Graph, filename: Optional[str] = None) -> None:
    """
    Visualize a graph using NetworkX.

    Args:
        graph: The graph to visualize.
        filename: Optional filename to save the visualization to. If not provided, the visualization will be displayed.
    """
    # Convert the graph to a NetworkX MultiDiGraph
    nx_graph = _to_networkx(graph)

    # Calculate the size of each node
    node_sizes = _get_node_sizes(nx_graph)

    # Define the connection style for the edges
    connection_style = _get_connection_style(nx_graph)

    # Calculate the position of each node in the graph
    pos = _get_node_positions(nx_graph)

    # Add the nodes
    nx.draw_networkx_nodes(
        nx_graph,
        pos,
        node_size=[node_sizes[n] for n in nx_graph.nodes],
        node_color="#EDF497",
        edgecolors="k",
    )

    # Add the edges
    nx.draw_networkx_edges(
        nx_graph,
        pos,
        node_size=[node_sizes[n] for n in nx_graph.nodes],
        connectionstyle=connection_style,
    )

    # Add the node labels
    nx.draw_networkx_labels(
        nx_graph,
        pos,
        labels=nx.get_node_attributes(nx_graph, "label"),
    )

    # Add the edge labels
    nx.draw_networkx_edge_labels(
        nx_graph,
        pos,
        edge_labels=nx.get_edge_attributes(nx_graph, "label"),
        connectionstyle=connection_style,
    )

    # NetworkX isn't brilliant at setting the axis limits, so we'll do it manually
    plt.xlim(
        min(arr[0] for arr in pos.values()) - AXIS_BUFFER,
        max(arr[0] for arr in pos.values()) + AXIS_BUFFER,
    )
    plt.ylim(
        min(arr[1] for arr in pos.values()) - AXIS_BUFFER,
        max(arr[1] for arr in pos.values()) + AXIS_BUFFER,
    )

    plt.axis("off")

    if filename:
        plt.savefig(filename)
    else:
        plt.show()


@typechecked
def _to_networkx(graph: Graph) -> nx.MultiDiGraph:
    """
    Convert a Graph object to a NetworkX MultiDiGraph.

    Args:
        graph: The graph to convert.

    Returns:
        The NetworkX MultiDiGraph representation of the graph.
    """
    # Define a directed graph
    # Use a MultiDiGraph to allow multiple edges between nodes
    nx_graph = nx.MultiDiGraph()

    if len(graph.external_input) > 0:
        # Add a node to represent the user input
        nx_graph.add_node(graph.external_input_id, label="User Input")

    for node in graph.nodes["nodes"]:
        # Add the node to the graph with its label
        nx_graph.add_node(node, label=node)

        # Loop through the inputs to the node and add edges
        for input_key, input_value in graph.nodes["nodes"][node]["inputs"].items():
            nx_graph.add_edge(input_value["node_name"], node, label=input_key)

    return nx_graph


@typechecked
def _get_node_sizes(graph: nx.MultiDiGraph) -> dict:
    """
    Calculate the size of each node based on the length of the label.

    Args:
        graph: The NetworkX graph.

    Returns:
        A dictionary mapping node names to node sizes.
    """
    return {
        node: MINIMUM_NODE_SIZE + len(label) * NODE_SIZE_SCALE
        for node, label in nx.get_node_attributes(graph, "label").items()
    }


@typechecked
def _get_connection_style(
    graph: nx.MultiDiGraph, connection_arc: float = MINIMUM_CONNECTION_ARC
) -> list:
    """
    Calculate the connection style for each edge based on the number of connections. If there is only one connection
    between two nodes, the connection style is a straight line. If there are multiple connections, the connection styles
    are arcs with increasing radii.

    Args:
        graph: The NetworkX graph.
        connection_arc: The arc length for the connection style.

    Returns:
        List of connection styles.
    """
    # Calculate the maximum number of connections between any two nodes
    max_edge_connectivity = 0
    for s, t in it.combinations(graph, 2):
        if graph.has_edge(s, t):
            max_edge_connectivity = max(
                max_edge_connectivity, len(graph.get_edge_data(s, t))
            )

    # Define the connection style for the edges based on the maximum number of connections
    connection_style = ["arc3,rad=0"]
    connection_style += [
        f"arc3,rad={r}"
        for r in it.accumulate([connection_arc] * (max_edge_connectivity - 1))
    ]

    return connection_style


@typechecked
def _get_node_positions(graph: nx.MultiDiGraph) -> dict:
    """
    Calculate the position of each node in the graph.

    Args:
        graph: The NetworkX graph.

    Returns:
        A dictionary mapping node names to node positions.
    """

    in_degrees = graph.in_degree()

    # Try and use a breadth-first search layout starting from a node with no incoming edges
    pos = None
    for node_degree in in_degrees:
        if node_degree[1] == 0:
            # Found a node with no incoming edges - use it as the starting point
            pos = nx.bfs_layout(graph, node_degree[0])
            break

    # If no node with no incoming edges was found, use a spring layout
    if pos is None:
        pos = nx.spring_layout(graph, seed=42)

    return pos
