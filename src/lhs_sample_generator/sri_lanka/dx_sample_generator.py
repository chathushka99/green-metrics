from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------
# 1) Base params (corrected)
# ------------------------------------------------
params_DX_base = [
    None, None, None,
    0.92,    # 3 UPS_e
    0.03,    # 4 PD_lr
    0.03,    # 5 L_percentage
    0.95,    # 6 SHR
    10.0,    # 7 delta_T_air
    800,     # 8 Fan_Pressure_CRAC
    0.675,   # 9 Fan_e_CRAC
    27,      # 10 T_up (fixed)
    18,      # 11 T_lw (fixed)
    15,      # 12 dp_up (fixed)
    -9,      # 13 dp_lw (fixed)
    0.20,    # 14 RH_up (UPDATED)
    0.60,    # 15 RH_lw (UPDATED)
    0.0      # 16 pcop
]

# ------------------------------------------------
# 2) Parameter ranges (corrected)
# ------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),   # 3 UPS_e
    (0.02, 0.04),   # 4 PD_lr
    (0.02, 0.04),   # 5 L_percentage
    (0.90, 0.99),   # 6 SHR
    (8.0, 12.0),    # 7 delta_T_air
    (300, 1200),    # 8 Fan_Pressure_CRAC ✅ FIXED
    (0.60, 0.75),   # 9 Fan_e_CRAC
    None,           # 10 fixed
    None,           # 11 fixed
    None,           # 12 fixed
    None,           # 13 fixed
    (0.10, 0.30),   # 14 RH_up ✅ NOW VARIABLE
    (0.54, 0.66),   # 15 RH_lw ✅ NOW VARIABLE
    (-0.45, 0.20)   # 16 pcop
]

assert len(params_DX_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------
# 3) Extract active params
# ------------------------------------------------
active_ranges = []
active_positions = []

for idx, r in enumerate(param_ranges):
    if isinstance(r, tuple):
        active_ranges.append(r)
        active_positions.append(idx)

n_vars = len(active_ranges)
n_samples = 50

# ------------------------------------------------
# 4) LHS sampling
# ------------------------------------------------
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# ------------------------------------------------
# 5) Scale
# ------------------------------------------------
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])
scaled = mins + (maxs - mins) * unit_samples

# ------------------------------------------------
# 6) Build dataset
# ------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_DX_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])

# ------------------------------------------------
# 7) Save
# ------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "data" / "lhs_samples" / "sri_lanka" / "dx_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

pd.DataFrame(all_samples).to_csv(output_path, index=False)

print(f"Saved: {output_path}")
