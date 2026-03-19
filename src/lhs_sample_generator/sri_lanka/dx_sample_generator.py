from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------
# 1) Base params for DX (only vector length matters)
# ------------------------------------------------
params_DX_base = [
    None, None, None,
    0.81, 0.03, 0.03, 0.97,
    5.8, 500, 0.675,
    24.75, 20.25,
    15.0, -1.5,
    20, 60,
    0.375
]

# ------------------------------------------------
# 2) Case 10 (Small) ranges
# ------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),  # idx 3 (%)
    (0.02, 0.04),  # idx 4 (%)
    (0.02, 0.04),  # idx 5 (%)
    (0.90, 1.00),  # idx 6 (%)
    (8, 12),  # idx 7 (°C assumed)
    (400, 600),  # idx 8 (Pa assumed)
    (0.60, 0.75),  # idx 9 (%)
    None,  # idx10 fixed 27
    None,  # idx11 fixed 18
    None,  # idx12 fixed 15
    None,  # idx13 fixed -9
    None,  # idx14 fixed 0.07
    None,  # idx15 fixed 0.08
    (-0.45, 0.20)  # idx16 (%)
]

assert len(params_DX_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------
# 3) Latin Hypercube Sampling setup
# ------------------------------------------------
active_ranges = []
active_positions = []

for idx, r in enumerate(param_ranges):
    if isinstance(r, tuple):
        active_ranges.append(r)
        active_positions.append(idx)

n_vars = len(active_ranges)
n_samples = 50

# Generate unit LHS samples in [0,1]
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# Scale to real ranges
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])
scaled = mins + (maxs - mins) * unit_samples

# ------------------------------------------------
# 4) Build full sample vectors
# ------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_DX_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)

# ------------------------------------------------
# 5) Save to CSV
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "sri_lanka" / "dx_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
