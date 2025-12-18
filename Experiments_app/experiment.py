import time
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import pickle



# ======= PATHS (change if needed) ======================

AIRPORTS_PATH = "/Users/xvvvvx/Documents/UCB/INDENG 240/Project/Experiments/airports_clean.csv"      # e.g. data/airports_clean.csv
GRAPH_PATH    = "/Users/xvvvvx/Documents/UCB/INDENG 240/Project/Experiments/flight_graph_with_capacity.gpickle"

# ======= 1. Load data ==================================

def load_airports():
    return pd.read_csv(AIRPORTS_PATH)

def load_graph():
    with open(GRAPH_PATH, "rb") as f:
        G = pickle.load(f)
    return G


# ======= 2. Switch between base/low/high scenarios =====

def set_capacity_scenario(G, scenario="base"):
    """
    scenario: "base" -> use 'capacity'
              "low"  -> use 'capacity_low'
              "high" -> use 'capacity_high'

    This copies the chosen scenario into edge['capacity'],
    which is what NetworkX's max flow will read.
    """
    attr_name = {
        "base": "capacity",
        "low": "capacity_low",
        "high": "capacity_high"
    }[scenario]

    for u, v, data in G.edges(data=True):
        # fall back to base if the chosen attribute is missing
        base_cap = data.get("capacity", 1.0)
        data["capacity"] = float(data.get(attr_name, base_cap))

    return G

# ======= 3. Max-flow + min-cut =========================

def run_max_flow(G, source, sink, algo="edmonds_karp"):
    """
    algo in {"edmonds_karp", "preflow_push"}.
    Returns: flow_value, cut_value, cut_edges, runtime
    """
    if algo == "edmonds_karp":
        flow_func = nx.algorithms.flow.edmonds_karp
    elif algo == "preflow_push":
        flow_func = nx.algorithms.flow.preflow_push
    else:
        raise ValueError("Unsupported algo: {}".format(algo))

    t0 = time.time()
    flow_value, flow_dict = nx.maximum_flow(
        G, _s=source, _t=sink, capacity="capacity", flow_func=flow_func
    )
    runtime = time.time() - t0

    # min cut
    cut_value, (S, T) = nx.minimum_cut(G, source, sink, capacity="capacity")
    cut_edges = []
    for u in S:
        for v in G.successors(u):
            if v in T and G[u][v]["capacity"] > 0:
                cut_edges.append((u, v))

    return flow_value, cut_value, cut_edges, runtime

# ======= 4. Helpers for pretty tables ==================

def airport_label(iata, airports_df):
    row = airports_df[airports_df["iata"] == iata]
    if row.empty:
        return iata
    r = row.iloc[0]
    return f"{iata} ({r['city']}, {r['country']})"

def summarize_cut_edges(cut_edges, airports_df, G, top_k=10):
    records = []
    for (u, v) in cut_edges:
        cap = G[u][v].get("capacity", 1.0)
        records.append({
            "u": u,
            "v": v,
            "u_label": airport_label(u, airports_df),
            "v_label": airport_label(v, airports_df),
            "capacity": cap
        })
    # tightest bottlenecks first
    records.sort(key=lambda x: x["capacity"])
    return records[:top_k]

# ======= 5. Disruption scenario ========================

def apply_hub_disruption(G, hub, factor=0.3):
    """
    Return a copy of G where all edges in/out of 'hub'
    have capacity multiplied by 'factor'.
    """
    H = G.copy()
    for u, v, data in H.in_edges(hub, data=True):
        if "capacity" in data:
            data["capacity"] *= factor
    for u, v, data in H.out_edges(hub, data=True):
        if "capacity" in data:
            data["capacity"] *= factor
    return H

# ======= 6. Simple plotting function ===================

def plot_flow_before_after(results, title):
    """
    results: list of dicts { 'od': 'JFK-LAX', 'before': x, 'after': y }
    """
    ods = [r["od"] for r in results]
    before_vals = [r["before"] for r in results]
    after_vals  = [r["after"] for r in results]

    x = range(len(ods))
    width = 0.35

    plt.figure(figsize=(8, 4))
    plt.bar([xi - width/2 for xi in x], before_vals, width, label="Before")
    plt.bar([xi + width/2 for xi in x], after_vals, width, label="After")
    plt.xticks(x, ods)
    plt.ylabel("Max flow (seats / time unit)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()

# ======= 7. Main: your experiments =====================

def main():
    airports_df = load_airports()
    G = load_graph()

    # choose scenario here: "base", "low", "high"
    scenario = "base"
    G = set_capacity_scenario(G, scenario=scenario)

    od_pairs = [
        ("JFK", "LAX"),
        ("SFO", "ORD"),
        ("LHR", "DXB"),
    ]
    algos = ["edmonds_karp", "preflow_push"]

    print(f"=== Scenario: {scenario} ===")
    all_results = []

    for (s, t) in od_pairs:
        for algo in algos:
            print(f"\nO/D = {s} -> {t}, algo = {algo}")
            flow_value, cut_value, cut_edges, runtime = run_max_flow(G, s, t, algo=algo)
            print(f"  max flow       = {flow_value:.2f}")
            print(f"  min-cut value  = {cut_value:.2f}")
            print(f"  runtime (sec)  = {runtime:.4f}")

            top_edges = summarize_cut_edges(cut_edges, airports_df, G, top_k=5)
            print("  Top bottleneck edges in min-cut:")
            for rec in top_edges:
                print(f"    {rec['u_label']} -> {rec['v_label']}, cap={rec['capacity']:.1f}")

            all_results.append({
                "od": f"{s}-{t}",
                "algo": algo,
                "flow": flow_value,
                "cut": cut_value,
                "runtime": runtime
            })

    # --- disruption experiment: hit one hub ---
    hub = "ORD"
    factor = 0.3
    G_dis = apply_hub_disruption(G, hub, factor=factor)

    print(f"\n=== Disruption at {hub}, factor={factor} ===")
    disruption_summary = []
    for (s, t) in od_pairs:
        flow_before, _, _, _ = run_max_flow(G, s, t, algo="preflow_push")
        flow_after,  _, _, _ = run_max_flow(G_dis, s, t, algo="preflow_push")
        print(f"  {s}->{t}: before={flow_before:.2f}, after={flow_after:.2f}")
        disruption_summary.append({
            "od": f"{s}-{t}",
            "before": flow_before,
            "after": flow_after
        })

    plot_flow_before_after(
        disruption_summary,
        title=f"Max flow before vs after disruption at {hub} ({scenario} capacity)"
    )

if __name__ == "__main__":
    main()
