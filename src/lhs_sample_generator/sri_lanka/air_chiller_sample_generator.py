from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameters (length + reasonable defaults)
# ------------------------------------------------------
params_AIRChiller_base = [
    None, None, None,
    0.92,     # 3 UPS_e
    0.035,    # 4 PD_lr
    0.035,    # 5 L_percentage
    0.97,     # 6 SHR (UPDATED)
    10.0,     # 7 delta_T_air
    800,      # 8 Fan_Pressure_CRAC
    0.70,     # 9 Fan_e_CRAC
    6500000,  # 10 Pump_Pressure_HD (UPDATED SCALE)
    0.70,     # 11 Pump_e_HD
    0.75,     # 12 HTE
    11.0,     # 13 delta_T_water
    145000,   # 14 Pump_Pressure_CW
    0.70,     # 15 Pump_e_CW
    0.30,     # 16 Chiller_load
    -0.10,    # 17 pcop (UPDATED RANGE)
    27,       # 18 T_up (fixed)
    18,       # 19 T_lw (fixed)
    15,       # 20 dp_up (fixed)
    -9,       # 21 dp_lw (fixed)
    0.20,     # 22 RH_up (NOW VARIABLE)
    0.70      # 23 RH_lw (NOW VARIABLE)
]

# ------------------------------------------------------
# 2) Parameter ranges (FINAL UPDATED)
# ------------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),        # 3 UPS_e
    (0.02, 0.05),        # 4 PD_lr
    (0.02, 0.05),        # 5 L_percentage
    (0.95, 0.99),        # 6 SHR
    (8.0, 12.0),         # 7 delta_T_air
    (300, 1200),         # 8 Fan_Pressure_CRAC
    (0.60, 0.80),        # 9 Fan_e_CRAC
    (6000000, 7000000),  # 10 Pump_Pressure_HD
    (0.60, 0.80),        # 11 Pump_e_HD
    (0.65, 0.90),        # 12 HTE
    (10.0, 12.0),        # 13 delta_T_water
    (114900, 172400),    # 14 Pump_Pressure_CW
    (0.60, 0.80),        # 15 Pump_e_CW
    (0.10, 0.50),        # 16 Chiller_load
    (-0.40, 0.25),       # 17 pcop (UPDATED)
    None,                # 18 T_up (fixed)
    None,                # 19 T_lw (fixed)
    None,                # 20 dp_up (fixed)
    None,                # 21 dp_lw (fixed)
    (0.10, 0.30),        # 22 RH_up
    (0.60, 0.80)         # 23 RH_lw
]

assert len(params_AIRChiller_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------------
# 3) Identify active parameters
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
# 4) Latin Hypercube Sampling
# ------------------------------------------------------
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# ------------------------------------------------------
# 5) Scale samples
# ------------------------------------------------------
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])

scaled = mins + (maxs - mins) * unit_samples

# ------------------------------------------------------
# 6) Build full parameter vectors
# ------------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_AIRChiller_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])

# ------------------------------------------------------
# 7) Save CSV
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "data" / "lhs_samples" / "sri_lanka" / "air_chiller_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
