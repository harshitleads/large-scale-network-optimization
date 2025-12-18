import matplotlib.pyplot as plt
import networkx as nx

def plot_st_subgraph_simple(G_sub, s, t):
    pos = nx.spring_layout(G_sub, seed=42)

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_edges(G_sub, pos, alpha=0.5)

    nx.draw_networkx_nodes(
        G_sub,
        pos,
        node_size=1800,
        node_color="steelblue",
        edgecolors="black"
    )

    nx.draw_networkx_labels(G_sub, pos, font_size=12, font_color="white")

    plt.title(f"Subgraph for {s} -> {t}")
    plt.axis("off")
    plt.show()

def plot_st_subgraph_simple(G_sub, s, t):
    pos = nx.spring_layout(G_sub, seed=42)

    plt.figure(figsize=(10, 8))
    nx.draw_networkx_edges(G_sub, pos, alpha=0.5)

    nx.draw_networkx_nodes(
        G_sub,
        pos,
        node_size=1800,
        node_color="steelblue",
        edgecolors="black"
    )

    nx.draw_networkx_labels(G_sub, pos, font_size=12, font_color="white")

    plt.title(f"Subgraph for {s} → {t}")
    plt.axis("off")

    plt.savefig(f"subgraph_{s}_{t}.png", dpi=300, bbox_inches="tight")
    plt.close()