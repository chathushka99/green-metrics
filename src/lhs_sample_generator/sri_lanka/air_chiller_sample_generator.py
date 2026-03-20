from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameters for AIR Chiller (only vector length)
# ------------------------------------------------------
params_AIRChiller_base = [
    None, None, None,
    0.86, 0.03, 0.05, 0.95,
    9.5, 650, 0.6,
    200000, 0.65,
    0.69,
    6.9,
    150000, 0.75,
    0.5,
    0.091,
    29, 15,
    16, 10,
    72, 26
]

# ------------------------------------------------------
# 2) Ranges for Case 7 (Midsize)
# ------------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),  # idx 3 (%)
    (0.02, 0.05),  # idx 4 (%)
    (0.02, 0.05),  # idx 5 (%)
    (0.90, 1.00),  # idx 6 (%)
    (8, 12),  # idx 7 (°C)
    (300, 1200),  # idx 8 (Pa)
    (0.60, 0.80),  # idx 9 (%)
    (6000000, 7000000),  # idx10 (Pa)
    (0.60, 0.80),  # idx11 (%)
    (0.65, 0.90),  # idx12 (-)
    (10, 12),  # idx13 (°C)
    (114900, 172400),  # idx14 (Pa)
    (0.60, 0.80),  # idx15 (%)
    (0.10, 0.50),  # idx16 (-)
    (-0.40, 0.00),  # idx17 (%)
    None,  # idx18 fixed (°C)
    None,  # idx19 fixed (°C)
    None,  # idx20 fixed (°C)
    None,  # idx21 fixed (°C)
    None,  # idx22 fixed (%)
    None  # idx23 fixed (%)
]

assert len(params_AIRChiller_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------------
# 3) Build list of ranged parameters
# ------------------------------------------------------
active_ranges = []
active_positions = []

for idx, r in enumerate(param_ranges):
    if isinstance(r, tuple):
        active_ranges.append(r)
        active_positions.append(idx)

n_vars = len(active_ranges)
n_samples = 50

# ------------------------------------------------------
# 4) Latin Hypercube Sampling (unit scale)
# ------------------------------------------------------
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# ------------------------------------------------------
# 5) Scale to the actual ranges
# ------------------------------------------------------
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])
scaled = mins + (maxs - mins) * unit_samples

# ------------------------------------------------------
# 6) Insert sampled values into full parameter vectors
# ------------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_AIRChiller_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])  # show first 3 samples

# ------------------------------------------------------
# 7) Save to CSV
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "sri_lanka" / "air_chiller_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
