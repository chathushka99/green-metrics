"""Compare model predictions with reference values produced by scikit-learn 0.22.2.

Usage: python tests/check_models.py path/to/ref.json
"""
import json
import sys
from pathlib import Path

import numpy as np

from green_metrics.simulation.dc import load_gp_model

ref = json.loads(Path(sys.argv[1]).read_text())
for name, d in ref.items():
    m = load_gp_model(f"{name}.pkl")
    y = m.predict(np.array(d["X"]))
    err = np.abs(y - np.array(d["y"])).max()
    print(f"{name}: max abs diff {err:.2e}")
    assert err < 1e-6, name
print("OK")
