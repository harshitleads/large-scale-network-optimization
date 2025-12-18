# Experiments_app/src/subgraph_utils.py

from typing import List
import networkx as nx
from itertools import islice

def k_shortest_paths_subgraph(G, source: str, sink: str, k: int = 3) -> nx.DiGraph:
    """
    Build a subgraph containing the union of up to k simple paths
    from source to sink (shortest in terms of hops).

    Uses islice to avoid enumerating all simple paths in a huge graph.
    """
    try:
        # Take only the first k shortest simple paths (generator)
        path_gen = nx.shortest_simple_paths(G, source, sink)
        paths = list(islice(path_gen, k))
    except nx.NetworkXNoPath:
        return nx.DiGraph()  # empty subgraph if no path

    nodes = set()
    edges = set()
    for path in paths:
        nodes.update(path)
        for u, v in zip(path[:-1], path[1:]):
            edges.add((u, v))

    H = nx.DiGraph()
    for n in nodes:
        H.add_node(n)
    for u, v in edges:
        if G.has_edge(u, v):
            H.add_edge(u, v, **G[u][v])

    return H