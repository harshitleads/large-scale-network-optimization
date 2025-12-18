
from typing import List, Dict, Tuple
from .flow_utils import run_max_flow
from .scenarios import apply_hub_disruption


def run_algo_comparison(
    G,
    od_pairs: List[Tuple[str, str]],
    algos: List[str],
    verbose: bool = True,
) -> List[Dict]:
    """
    Run max-flow with multiple algorithms on multiple O/D pairs.
    Returns a list of dicts with results.
    """
    results = []

    for s, t in od_pairs:
        for algo in algos:
            flow, cut, _, t_runtime = run_max_flow(G, s, t, algo=algo)
            if verbose:
                print(s, t, algo, flow, t_runtime)
            results.append({
                "source": s,
                "sink": t,
                "algorithm": algo,
                "max_flow": flow,
                "min_cut": cut,
                "runtime": t_runtime,
            })

    return results