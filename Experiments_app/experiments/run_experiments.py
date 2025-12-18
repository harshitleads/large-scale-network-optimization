import os
import sys
import pandas as pd

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

AIRPORTS_PATH = os.path.join(PROJECT_ROOT, "data", "airports_clean.csv")
GRAPH_PATH    = os.path.join(PROJECT_ROOT, "data", "flight_graph_with_capacity.gpickle")

from src.io_utils import load_airports, load_graph
from src.flow_utils import run_max_flow
from src.scenarios import set_capacity_scenario, apply_hub_disruption
from src.plotting import plot_flow_before_after
from src.run_disruption_experiment import run_disruption_experiment
from src.run_algo_comparison import run_algo_comparison
from src.weakness_analysis import find_weakest_edge_and_node

def main():
    # 1. Load data
    airports = load_airports(AIRPORTS_PATH)
    G = load_graph(GRAPH_PATH)

    # 2. Choose capacity scenario
    G = set_capacity_scenario(G, "low")

    # 3. Define O/D pairs and algorithms
    od_pairs = [("JFK", "LAX"), ("ATL", "SFO"), ("ORD", "SEA")]
    algos = ["edmonds_karp", "preflow_push"]
    
    # 4. Run algorithm comparison experiment
    algo_results = run_algo_comparison(G, od_pairs, algos, verbose=True)
    pd.DataFrame(algo_results).to_csv("algo_comparison.csv")
    
    # # 5. Run disruption experiment at ORD
    disruption_results, G_dis = run_disruption_experiment(
        G,
        od_pairs,
        hub="ATL",
        factor=0.3,
        algo="preflow_push",
        verbose=True,
    )
    
    # 6. Plot before/after flows for disruption
    plot_flow_before_after(disruption_results, "ATL disruption")
    
    # 7. Find weakest edge and node
    print("\n=== Weakest edge & node per O/D pair ===")

    for s, t in od_pairs:
        info = find_weakest_edge_and_node(G_dis, s, t, algo="preflow_push")

        print(f"{s} -> {t}")
        print(f"  max flow = {info['flow_value']}")
        print(f"  min cut = {info['cut_value']}")
        if info["weakest_edge"] is not None:
            u, v, cap = info["weakest_edge"]
            print(f"  weakest edge = {u} -> {v}, capacity = {cap}")

        if info["weakest_node"] is not None:
            node, total_cap = info["weakest_node"]
            print(f"  weakest node = {node}, total adjacent cut cap = {total_cap}")

if __name__ == "__main__":
    main()