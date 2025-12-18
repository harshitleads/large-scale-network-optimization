import os
import sys

# ---- add PROJECT ROOT (Experiments_app) to Python path ----
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))  # one level up: Experiments_app
sys.path.insert(0, PROJECT_ROOT)

print("PROJECT_ROOT =", PROJECT_ROOT)
print("sys.path[0] =", sys.path[0])