"""
capacity_model.py

Capacity modeling for the OpenFlights directed route network.

Goal
----
Turn each directed route (u -> v) into an edge capacity that can be used for
max-flow / min-cut (and robust variants).

We treat OpenFlights "routes" as *direct* connections operated by an airline
(with an optional aircraft equipment code). Because the cleaned routes file is
deduplicated, each row is interpreted as one distinct "service option"
(airline and/or equipment) on that directed edge.

Main idea (simple + defensible)
-------------------------------
1) Frequency proxy:
   - Use the number of distinct airlines operating on an edge as a proxy for
     how much service/frequency the market supports.
   - If airline codes are missing, fall back to the number of route records
     on that edge.

2) Seats proxy (optional):
   - If equipment codes are present, map the aircraft type to an approximate
     seat count (typical single-class capacity).
   - If the equipment is unknown, use a conservative default.

3) Capacity:
     capacity(u,v) = freq_proxy(u,v) * seat_proxy(u,v)

4) Uncertainty (robust interval):
     capacity_low  = (1 - delta) * capacity
     capacity_high = (1 + delta) * capacity
   Default delta = 0.30  ->  [0.7c, 1.3c]

This is not "true" physical capacity; it is a consistent, reproducible proxy
for optimization experiments, using only the fields available in OpenFlights.
"""

from __future__ import annotations

import argparse
import pickle
import re
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

import pandas as pd
import networkx as nx


# --- Seat estimates (typical single-class / average configs) ---
# Add / adjust as needed. Unknown codes fall back to default_seats.
SEAT_MAP: Dict[str, int] = {
    # Airbus
    "A319": 140, "A320": 180, "A321": 200, "A330": 280, "A340": 300, "A350": 320, "A380": 500,
    "319": 140, "320": 180, "321": 200, "330": 280, "340": 300, "350": 320, "380": 500,

    # Boeing
    "B717": 120, "B727": 150, "B737": 160, "B738": 170, "B739": 180,
    "B747": 410, "B757": 200, "B767": 250, "B777": 350, "B787": 290,
    "717": 120, "727": 150, "737": 160, "738": 170, "739": 180,
    "747": 410, "757": 200, "767": 250, "777": 350, "787": 290,

    # Regional / common
    "CR2": 50, "CRJ": 70, "CR7": 70, "CR9": 90,
    "E70": 70, "E75": 76, "E90": 90, "E95": 100,
    "ER4": 50, "ERJ": 50, "DH4": 78, "AT7": 70, "AT4": 46,
    "SF3": 30, "SF2": 19,
}


@dataclass(frozen=True)
class CapacityConfig:
    freq_proxy: str = "airlines"   # "airlines" or "routes"
    use_equipment: bool = True
    default_seats: int = 150
    delta: float = 0.30            # uncertainty half-width


def _first_equipment_token(equipment: str) -> Optional[str]:
    """
    Extract a plausible first aircraft code from an equipment string.

    OpenFlights equipment can be like:
      "320", "A320", "CR2", "320 321", "B738/B739", "E90|E95", etc.
    We take the first token split on common delimiters.
    """
    if equipment is None or (isinstance(equipment, float) and pd.isna(equipment)):
        return None
    s = str(equipment).strip()
    if not s:
        return None
    # Split on spaces and common separators
    token = re.split(r"[ \t;/|,]+", s)[0].strip()
    return token or None


def _seat_estimate_for_edge(equipment_series: pd.Series, default_seats: int) -> int:
    """
    Estimate seats for an edge by mapping equipment codes.
    If multiple equipment codes exist, take the rounded mean of known estimates.
    """
    seats = []
    for eq in equipment_series.dropna().astype(str):
        tok = _first_equipment_token(eq)
        if tok is None:
            continue
        # Normalize: remove dashes, upper-case
        key = tok.upper().replace("-", "")
        if key in SEAT_MAP:
            seats.append(SEAT_MAP[key])
        else:
            # Sometimes codes are like "73H" or "7M8" (B737-MAX8), etc.
            # We keep it simple and ignore unknowns.
            pass
    if seats:
        return int(round(sum(seats) / len(seats)))
    return int(default_seats)


def build_capacity_table(routes: pd.DataFrame, cfg: CapacityConfig) -> pd.DataFrame:
    """
    Build an edge-level capacity table from the cleaned routes DataFrame.

    Expected routes columns:
      - source_airport, dest_airport
      - airline (string airline code)
      - equipment (optional)
    """
    required = {"source_airport", "dest_airport"}
    missing = required - set(routes.columns)
    if missing:
        raise ValueError(f"routes is missing required columns: {sorted(missing)}")

    # Group by directed edge
    gb = routes.groupby(["source_airport", "dest_airport"], dropna=False)

    # Frequency proxy
    if cfg.freq_proxy == "airlines" and "airline" in routes.columns:
        freq = gb["airline"].nunique(dropna=True).rename("n_airlines")
        n_routes = gb.size().rename("n_routes")
        freq_proxy = freq.fillna(0).astype(int)
    else:
        n_routes = gb.size().rename("n_routes")
        freq_proxy = n_routes.rename("n_airlines")  # keep a consistent name downstream

    # Seat proxy
    if cfg.use_equipment and "equipment" in routes.columns:
        seat_est = gb["equipment"].apply(lambda s: _seat_estimate_for_edge(s, cfg.default_seats)).rename("seat_est")
    else:
        seat_est = pd.Series(cfg.default_seats, index=freq_proxy.index, name="seat_est")

    cap = (freq_proxy * seat_est).rename("capacity").astype(float)

    out = pd.concat([freq_proxy.rename("freq_proxy"), n_routes, seat_est, cap], axis=1).reset_index()
    out["capacity_low"] = (1.0 - cfg.delta) * out["capacity"]
    out["capacity_high"] = (1.0 + cfg.delta) * out["capacity"]
    return out


def add_capacities_to_graph(
    G: nx.DiGraph,
    routes: pd.DataFrame,
    cfg: CapacityConfig,
    *,
    overwrite: bool = True
) -> nx.DiGraph:
    """
    Add capacity attributes to a NetworkX DiGraph.

    Adds to each edge (u,v) if present:
      - capacity, capacity_low, capacity_high
      - freq_proxy, n_routes, seat_est
    """
    cap_tbl = build_capacity_table(routes, cfg)
    # Index for fast lookup
    cap_tbl = cap_tbl.set_index(["source_airport", "dest_airport"])

    missing_edges = 0
    for u, v in G.edges():
        if (u, v) not in cap_tbl.index:
            missing_edges += 1
            continue
        row = cap_tbl.loc[(u, v)]
        attrs = {
            "capacity": float(row["capacity"]),
            "capacity_low": float(row["capacity_low"]),
            "capacity_high": float(row["capacity_high"]),
            "freq_proxy": int(row["freq_proxy"]),
            "n_routes": int(row["n_routes"]),
            "seat_est": int(row["seat_est"]),
        }
        if overwrite:
            nx.set_edge_attributes(G, {(u, v): attrs})
        else:
            # only set keys that don't already exist
            existing = G.edges[u, v]
            for k, val in attrs.items():
                if k not in existing:
                    existing[k] = val

    if missing_edges:
        # Not fatal: the graph and routes may be filtered slightly differently.
        print(f"[capacity_model] Warning: {missing_edges} edges in graph not found in routes table.")
    return G


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Add capacity proxy attributes to a flight DiGraph.")
    p.add_argument("--routes", required=True, help="Path to routes_clean.csv")
    p.add_argument("--graph", required=True, help="Path to flight_graph.gpickle (NetworkX DiGraph)")
    p.add_argument("--out", required=True, help="Output path for updated .gpickle")
    p.add_argument("--freq-proxy", choices=["airlines", "routes"], default="airlines",
                   help="Which frequency proxy to use (default: airlines)")
    p.add_argument("--no-equipment", action="store_true", help="Ignore equipment codes and use default seats.")
    p.add_argument("--default-seats", type=int, default=150, help="Default seats when equipment is unknown.")
    p.add_argument("--delta", type=float, default=0.30, help="Uncertainty half-width; 0.30 -> [0.7c, 1.3c].")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    routes = pd.read_csv(args.routes)
    with open(args.graph, "rb") as f:
        G = pickle.load(f)

    cfg = CapacityConfig(
        freq_proxy=args.freq_proxy,
        use_equipment=not args.no_equipment,
        default_seats=args.default_seats,
        delta=args.delta,
    )

    add_capacities_to_graph(G, routes, cfg, overwrite=True)

    with open(args.out, "wb") as f:
        pickle.dump(G, f)

    print(f"[capacity_model] Saved graph with capacities to: {args.out}")
    print(f"[capacity_model] Example edge attributes:")
    # Print one example edge that has capacity
    for u, v, data in G.edges(data=True):
        if "capacity" in data:
            print(f"  {u} -> {v}: { {k: data[k] for k in ['capacity','capacity_low','capacity_high','freq_proxy','n_routes','seat_est']} }")
            break


if __name__ == "__main__":
    main()
