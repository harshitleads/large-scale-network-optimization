# src/scenarios.py

def set_capacity_scenario(G, scenario="base"):
    attr = {
        "base": "capacity",
        "low": "capacity_low",
        "high": "capacity_high"
    }[scenario]

    for _, _, data in G.edges(data=True):
        base = data.get("capacity", 1.0)
        data["capacity"] = int(round(float(data.get(attr, base))))   
    return G

def apply_hub_disruption(G, hub, factor=0.3):
    H = G.copy()
    for u, v, data in H.in_edges(hub, data=True):
        data["capacity"] = int(round(data["capacity"] * factor))
    for u, v, data in H.out_edges(hub, data=True):
        data["capacity"] = int(round(data["capacity"] * factor))
    return H