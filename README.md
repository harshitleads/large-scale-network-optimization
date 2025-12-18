# Stress Testing Capacity in the U.S. Domestic Airline Network

This repository contains all code, data, and experiments used in the IEOR 240 final project:
**“Stress Testing Capacity in the U.S. Domestic Airline Network.”**

The project models the U.S. domestic airline network as a directed capacitated graph and analyzes
structural robustness using max-flow/min-cut methods under capacity stress and hub disruption
scenarios.

## Contributors
- Harshit Sharma (UC Berkeley)
- Jiayang Hong (UC Berkeley)
- Victor Xu (UC Berkeley)
- Yiyang Wang (UC Berkeley)
---

## Repository Structure
.
├── data/
│   ├── airports_clean.csv
│   └── flight_graph_with_capacity.gpickle
│
├── capacity_modeling/
│   ├── build_graph.py           # Constructs NetworkX graph from cleaned CSVs
│   └── capacity_utils.py        # Seat-capacity construction logic
│
├── src/
│   ├── io_utils.py              # Data loading utilities
│   ├── flow_utils.py            # Max-flow solvers (Edmonds–Karp, preflow–push)
│   ├── scenarios.py             # Capacity scaling and hub disruption logic
│   ├── weakness_analysis.py     # Min-cut decomposition and weakest edge/node detection
│   ├── plotting.py              # Bar plots for disruption experiments
│   └── plotting_path.py         # Capacity-labeled subgraph visualization
│
├── experiments/
│   ├── run_experiments.py       # Main experiment driver
│   ├── graph.py                 # Subgraph construction for visualization
│   └── graph_copy.py            # Variant used during visualization debugging
│
└── README.md
---

## Data Description


- **Source**: OpenFlights public dataset  
Link: OpenFlights Database — https://openflights.org/data.php

- **Scope**: U.S. domestic airports and routes only
- **Preprocessing**:
  - Removed non-U.S. airports and international routes
  - Consolidated duplicate routes
  - Removed self-loops and invalid identifiers
  - Constructed directed edges representing scheduled service existence

Edge capacities represent **seat supply proxies**, not passenger demand.

### Capacity Modeling Pipeline

Raw and cleaned CSV datasets are transformed into a directed capacitated graph using scripts in the `capacity_modeling/` directory. These scripts construct the NetworkX graph by:

- Creating directed edges for each valid U.S. domestic route
- Aggregating multiple airline listings into a single edge
- Attaching seat-capacity attributes derived from aircraft and airline information
- Serializing the final graph to `flight_graph_with_capacity.gpickle` for reuse in experiments

This separation ensures that data preprocessing, capacity construction, and optimization experiments remain modular and reproducible.

---

## Datasets

This project uses publicly available airline route and airport data from the **OpenFlights** database. All datasets required to reproduce the results are included in the `data/` directory.

### Included Files

- `airports_clean.csv`  
  Cleaned list of U.S. domestic airports, including IATA codes and geographic metadata.  
  This file is derived from the OpenFlights airports dataset and filtered to retain only airports located within the United States.

- `routes_clean.csv`  
  Cleaned list of scheduled airline routes between U.S. airports.  
  Duplicate routes across airlines are consolidated, invalid airport identifiers are removed, and self-loops are excluded.

- `flight_graph_with_capacity.gpickle`  
  Serialized NetworkX directed graph representing the U.S. domestic airline network.  
  Nodes correspond to airports and edges correspond to directed flight routes with seat-capacity attributes constructed using the methodology described in the report.

### Data Preprocessing Summary

Raw OpenFlights data was preprocessed to:
- Restrict the network to U.S. domestic operations
- Remove duplicate and invalid routes
- Eliminate self-loops
- Consolidate multiple airline listings into a single directed edge
- Attach capacity attributes used in max-flow and min-cut analysis

All preprocessing scripts are included in the repository and can be re-run to regenerate the cleaned datasets.

## Capacity Modeling

Edge capacity is constructed as:
capacity(u, v) = (number of operating airlines) × (estimated seats per aircraft)
Three system-wide capacity scenarios are supported:
- **Low**: 30% reduction
- **Base**: nominal capacity
- **High**: 30% increase

These scenarios enable controlled stress testing under realistic operational perturbations.

---

## Algorithms Implemented

- **Edmonds–Karp** (augmenting-path method)
- **Preflow–Push** (push–relabel method)

Both algorithms return identical max-flow values. Runtime comparisons are reported for empirical
performance analysis.

---

## Hub Disruption Experiments

Partial hub disruption is modeled by scaling **all incoming and outgoing edge capacities** of a
selected airport by a multiplicative factor (e.g., 0.3).

This simulates:
- Severe weather
- Air traffic control constraints
- Staffing shortages

Disruption experiments are conducted for major hubs including **ORD** and **ATL**.

---

## Running the Experiments

### 1. Environment Setup

Create and activate the Conda environment:

conda create -n ml_env python=3.11
conda activate ml_env
pip install -r requirements.txt
(Required packages include networkx, numpy, pandas, and matplotlib.)

### 2. Run All Experiments

From the experiments/ directory:
python run_experiments.py

This script will:
	•	Run max-flow computations for selected O/D pairs
	•	Compare algorithm runtimes
	•	Perform hub disruption experiments
	•	Identify weakest edges and nodes from minimum cuts
	•	Generate figures used in the report# ieor240-airline-network
