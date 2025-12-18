# src/plotting.py
import matplotlib.pyplot as plt

def plot_flow_before_after(results, title):
    ods = [r["od"] for r in results]
    before = [r["before"] for r in results]
    after  = [r["after"] for r in results]

    x = range(len(ods))
    w = 0.35

    plt.figure(figsize=(8, 4))
    plt.bar([i - w/2 for i in x], before, w, label="Before")
    plt.bar([i + w/2 for i in x], after,  w, label="After")
    plt.xticks(x, ods)
    plt.ylabel("Max flow")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()