import pandas as pd
import pickle

def load_airports(path):
    return pd.read_csv(path)

def load_graph(path):
    with open(path, "rb") as f:
        G = pickle.load(f)
    return G
