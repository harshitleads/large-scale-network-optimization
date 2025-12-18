# src/flow_utils.py
import time
import networkx as nx

def run_max_flow(G, source, sink, algo="edmonds_karp"):
    if algo == "edmonds_karp":
        flow_func = nx.algorithms.flow.edmonds_karp
    elif algo == "preflow_push":
        flow_func = nx.algorithms.flow.preflow_push
    else:
        raise ValueError("Unknown algorithm")

    t0 = time.time()
    flow_value, _ = nx.maximum_flow(
        G, source, sink, capacity="capacity", flow_func=flow_func
    )
    runtime = time.time() - t0

    cut_value, (S, T) = nx.minimum_cut(G, source, sink, capacity="capacity")

    cut_edges = [
        (u, v)
        for u in S
        for v in G.successors(u)
        if v in T and G[u][v]["capacity"] > 0
    ]

    return flow_value, cut_value, cut_edges, runtime
