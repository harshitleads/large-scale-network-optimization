# Large-Scale Network Optimization

Max-flow and min-cut analysis of the U.S. domestic airline network, with hub disruption simulations to measure structural robustness under stress. Built for IEOR 240 at UC Berkeley.

---

## The Core Question

Hub-and-spoke airline networks are optimized for efficiency. But what happens when a major hub fails?

This project models the U.S. domestic airline network as a directed, capacitated graph and asks: how much passenger throughput can the network sustain, which routes and airports create hard bottlenecks, and how fragile is the system when a critical hub is disrupted?

---

## What We Built

A graph-based simulation pipeline using real FAA flight data to:

- Construct the network as a directed, capacitated graph (airports as nodes, routes as edges, seat capacity as edge weights)
- Run max-flow analysis between origin-destination pairs to find true throughput limits
- Identify minimum cuts — the smallest set of routes whose removal isolates parts of the network
- Simulate hub disruptions by reducing capacity on all edges connected to a major hub (e.g., ORD) and measuring the throughput drop
- Compare two flow algorithms: Edmonds-Karp (BFS-based, intuitive) and Preflow-Push (more efficient at scale)

---

## Key Findings

**Networks are more fragile than they look.** Bottlenecks are not always at the busiest airports. A single low-capacity route can limit flow across an entire region.

**Hub disruptions propagate.** Reducing capacity at one major hub by 70% caused significant throughput drops across unrelated origin-destination pairs — not just the ones routing through that hub directly.

**Algorithm choice matters at scale.** Preflow-Push outperformed Edmonds-Karp on runtime for large graphs while producing identical flow values, confirming correctness and demonstrating the practical value of algorithm selection for real-world network sizes.

---

## Modeling Assumptions

The FAA dataset does not include route-level seat capacities. We approximated capacity using aircraft type mappings (e.g., Boeing 737 approx 160 seats, Airbus A320 approx 150 seats). This is a deliberate modeling tradeoff: reduced realism in exchange for tractability. The structural findings hold under this assumption.

---

## Stack

- Language: Python
- Graph library: NetworkX
- Data: FAA domestic flight routes and aircraft type records

---

## Repo Structure

```
data/           FAA flight routes and aircraft capacity mappings
notebooks/      Full pipeline: graph construction, flow analysis, disruption simulations
report/         Final project report (PDF)
```

---

## The Broader Insight

Highly optimized networks are often the most fragile. Redundancy and efficiency trade off directly. This project makes that tradeoff quantifiable rather than theoretical.

---

## Contributors

Harshit Sharma, Jiayang Hong, Victor Xu, Yiyang Wang — UC Berkeley MEng IEOR
