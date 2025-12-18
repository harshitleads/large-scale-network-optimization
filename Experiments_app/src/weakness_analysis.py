# Experiments_app/src/weakness_analysis.py

from typing import Dict, Tuple, Optional
from .flow_utils import run_max_flow

def find_weakest_edge_and_node(
    G,
    source: str,
    sink: str,
    algo: str = "preflow_push",
) -> Dict:
    """
    For a given (source, sink), compute the min-cut and identify:
      - weakest edge: min-capacity edge in the min-cut
      - weakest node: node incident to min-cut edges with smallest
                      total adjacent cut capacity
    """

    flow_value, cut_value, cut_edges, _ = run_max_flow(G, source, sink, algo=algo)

    # DEBUG: see what min-cut edges we got
    # (you can delete these prints later)
    # print(f"[DEBUG] {source}->{sink}: |cut_edges| = {len(cut_edges)}")

    if not cut_edges:
        # No edges crossing the cut (shouldn't happen when flow > 0,
        # but let's handle it gracefully).
        return {
            "source": source,
            "sink": sink,
            "flow_value": flow_value,
            "cut_value": cut_value,
            "weakest_edge": None,
            "weakest_node": None,
        }

    # ---------------- Weakest edge ----------------
    weakest_edge: Optional[Tuple[str, str, float]] = None
    min_cap = float("inf")

    for u, v in cut_edges:
        cap = G[u][v].get("capacity", 0.0)
        if cap < min_cap:
            min_cap = cap
            weakest_edge = (u, v, cap)

    # ---------------- Weakest node ----------------
    node_cut_capacity = {}

    for u, v in cut_edges:
        cap = G[u][v].get("capacity", 0.0)
        node_cut_capacity[u] = node_cut_capacity.get(u, 0.0) + cap
        node_cut_capacity[v] = node_cut_capacity.get(v, 0.0) + cap

    weakest_node = min(
        node_cut_capacity.items(),
        key=lambda item: item[1],
    )  # (node, total_capacity)

    return {
        "source": source,
        "sink": sink,
        "flow_value": flow_value,
        "cut_value": cut_value,
        "weakest_edge": weakest_edge,
        "weakest_node": weakest_node,
    }