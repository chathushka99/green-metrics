from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------
# 1) Base params for DX
# ------------------------------------------------
params_DX_base = [
    None, None, None,
    0.81,      # 3 UPS_e
    0.03,      # 4 PD_lr
    0.03,      # 5 L_percentage
    0.97,      # 6 SHR
    6.0,       # 7 delta_T_air
    500,       # 8 Fan_Pressure_CRAC
    0.675,     # 9 Fan_e_CRAC
    24.0,      # 10 T_up
    20.0,      # 11 T_lw
    15.0,      # 12 dp_up
    -10.0,     # 13 dp_lw
    0.20,      # 14 RH_up
    0.60,      # 15 RH_lw
    0.0        # 16 pcop
]

# ------------------------------------------------
# 2) Parameter ranges (from your table)
# ------------------------------------------------
param_ranges = [
    None, None, None,

    (0.77, 0.85),      # 3 UPS_e
    (0.02, 0.04),      # 4 PD_lr
    (0.02, 0.04),      # 5 L_percentage
    (0.95, 0.99),      # 6 SHR
    (5, 8),            # 7 delta_T_air
    (400, 600),        # 8 Fan_Pressure_CRAC
    (0.60, 0.75),      # 9 Fan_e_CRAC
    (22.5, 27),        # 10 T_up
    (18, 22.5),        # 11 T_lw
    (13.5, 16.5),      # 12 dp_up
    (-12, -9),         # 13 dp_lw
    (0.10, 0.30),      # 14 RH_up
    (0.54, 0.66),      # 15 RH_lw
    (-0.45, 0.20)      # 16 pcop
]

assert len(params_DX_base) == len(param_ranges)

# ------------------------------------------------
# 3) Extract active variables
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
# 4) Latin Hypercube Sampling
# ------------------------------------------------
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# ------------------------------------------------
# 5) Scale samples
# ------------------------------------------------
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])

scaled = mins + (maxs - mins) * unit_samples

# ------------------------------------------------
# 6) Build full parameter vectors
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
# 7) Save CSV
# ------------------------------------------------
# Gets the absolute path to the 'green-metrics' folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "usa" / "usa_dx_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
