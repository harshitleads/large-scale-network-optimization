import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.insert(0, PROJECT_ROOT)

AIRPORTS_PATH = os.path.join(PROJECT_ROOT, "data", "airports_clean.csv")
GRAPH_PATH    = os.path.join(PROJECT_ROOT, "data", "flight_graph_with_capacity.gpickle")

from src.io_utils import load_airports, load_graph   # you actually don't need airports now, but ok if it's still there
from src.scenarios import set_capacity_scenario
from src.subgraph_utils import k_shortest_paths_subgraph
from src.plotting_path import plot_st_subgraph_simple  # <-- use new function


def main():
    print(">>> main() started")

    # You don't strictly need airports anymore, but you can leave this if you want
    # airports = load_airports(AIRPORTS_PATH)

    G = load_graph(GRAPH_PATH)
    print(">>> graph loaded:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")

    G = set_capacity_scenario(G, "base")
    print(">>> capacity scenario set")

    od_pairs = [("JFK", "LAX")]

    for s, t in od_pairs:
        print(f">>> building subgraph for {s}->{t}")
        G_sub = k_shortest_paths_subgraph(G, s, t, k=10)
        print(">>> subgraph size:", G_sub.number_of_nodes(), "nodes,", G_sub.number_of_edges(), "edges")
        plot_st_subgraph_simple(G_sub, s, t)
        print(">>> plot function called")



if __name__ == "__main__":
    main()
