# Experiments_app/src/plotting_path.py

import matplotlib.pyplot as plt
import networkx as nx

def plot_st_subgraph_simple(
    G_sub,
    source: str,
    sink: str,
    title: str = None,
    capacity_attr: str = "capacity",
):
    """
    Plot a small subgraph between source and sink using a simple graph layout,
    with edge capacity shown as labels.
    """

    if title is None:
        title = f"Paths between {source} and {sink}"

    if G_sub.number_of_nodes() == 0:
        print(f"[WARN] Subgraph for {source}->{sink} is empty; nothing to plot.")
        return

    # Layout (deterministic for reproducibility)
    pos = nx.spring_layout(G_sub, seed=42)

    plt.figure(figsize=(7, 5))

    # ---- draw edges ----
    nx.draw_networkx_edges(G_sub, pos, width=1.2)

    # ---- draw nodes ----
    nx.draw_networkx_nodes(G_sub, pos, node_size=1000)

    # ---- draw node labels (IATA codes) ----
    nx.draw_networkx_labels(G_sub, pos, font_size=9)

    # ---- highlight source and sink ----
    if source in G_sub:
        nx.draw_networkx_nodes(
            G_sub, pos, nodelist=[source], node_size=2400
        )
    if sink in G_sub:
        nx.draw_networkx_nodes(
            G_sub, pos, nodelist=[sink], node_size=2400
        )

    # ---- edge capacity labels ----
    edge_labels = {}
    for u, v, data in G_sub.edges(data=True):
        cap = data.get(capacity_attr, None)
        if cap is not None:
            edge_labels[(u, v)] = f"{cap:.0f}"

    nx.draw_networkx_edge_labels(
        G_sub,
        pos,
        edge_labels=edge_labels,
        font_size=8,
        label_pos=0.5,
    )

    plt.title(title)
    plt.axis("off")
    plt.tight_layout()

    # Save for report
    filename = f"{source}_{sink}_subgraph_capacity.png"
    plt.savefig(filename, dpi=200)
    print(f">>> saved capacity-labeled graph to {filename}")

    plt.show()
