import os
import sys
from typing import List, Dict, Tuple
from .flow_utils import run_max_flow
from .scenarios import apply_hub_disruption

def run_disruption_experiment(
    G,
    od_pairs: List[Tuple[str, str]],
    hub: str = "ORD",
    factor: float = 0.3,
    algo: str = "preflow_push",
    verbose: bool = True,
):
    """
    Apply a capacity reduction at 'hub' and measure before/after flows
    for each O/D pair using the chosen algorithm.

    Returns:
        disruption_results: list of dicts with 'od', 'before', 'after'
        G_disrupted: the modified graph
    """
    G_dis = apply_hub_disruption(G, hub, factor=factor)

    disruption_results = []
    for s, t in od_pairs:
        before, *_ = run_max_flow(G, s, t, algo=algo)
        after,  *_ = run_max_flow(G_dis, s, t, algo=algo)
        if verbose:
            print(f"[{hub} x{factor}] {s}->{t}: before={before}, after={after}")
        disruption_results.append({
            "od": f"{s}-{t}",
            "before": before,
            "after": after,
        })

    return disruption_results, G_dis