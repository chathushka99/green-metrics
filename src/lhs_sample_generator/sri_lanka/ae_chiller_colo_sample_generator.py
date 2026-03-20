from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameters (vector length only)
# ------------------------------------------------------
params_AE_Chiller_base = [
    None, None, None,
    0.92,   # 3 UPS_e
    0.035,  # 4 PD_lr
    0.035,  # 5 L_percentage
    10.0,   # 6 delta_T_air
    800,    # 7 Fan_Pressure_CRAC
    0.70,   # 8 Fan_e_CRAC
    6500000, # 9 Pump_Pressure_HD (UPDATED SCALE)
    0.70,   # 10 Pump_e_HD
    4.5,    # 11 AT_CT
    0.30,   # 12 Chiller_load
    11.0,   # 13 delta_T_water
    145000, # 14 Pump_Pressure_CW
    0.70,   # 15 Pump_e_CW
    9.0,    # 16 delta_T_CT
    200000, # 17 Pump_Pressure_CT (mid of new range)
    0.70,   # 18 Pump_e_CT
    0.001,  # 19 Windage_p
    5.0,    # 20 CC
    300,    # 21 Fan_Pressure_CT
    0.70,   # 22 Fan_e_CT
    0.97,   # 23 SHR
    0.6,    # 24 LGRatio
    27,     # 25 T_up (fixed)
    18,     # 26 T_lw (fixed)
    15,     # 27 dp_up (fixed)
    -9,     # 28 dp_lw (fixed)
    0.20,   # 29 RH_up (UPDATED BASE)
    0.70,   # 30 RH_lw (UPDATED BASE)
    -0.20   # 31 pcop
]

# ------------------------------------------------------
# 2) Parameter ranges (UPDATED)
# ------------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),        # 3 UPS_e
    (0.02, 0.05),        # 4 PD_lr
    (0.02, 0.05),        # 5 L_percentage
    (8.0, 13.0),         # 6 delta_T_air
    (300, 1200),         # 7 Fan_Pressure_CRAC
    (0.60, 0.80),        # 8 Fan_e_CRAC
    (6000000, 7000000),  # 9 Pump_Pressure_HD (UPDATED)
    (0.60, 0.80),        # 10 Pump_e_HD
    (3.0, 6.0),          # 11 AT_CT
    (0.10, 0.50),        # 12 Chiller_load
    (10.0, 12.0),        # 13 delta_T_water
    (114900, 172400),    # 14 Pump_Pressure_CW
    (0.60, 0.80),        # 15 Pump_e_CW
    (5.0, 13.0),         # 16 delta_T_CT
    (166900, 250400),    # 17 Pump_Pressure_CT (UPDATED)
    (0.60, 0.80),        # 18 Pump_e_CT
    (0.000005, 0.003),   # 19 Windage_p
    (3.0, 7.0),          # 20 CC
    (200, 400),          # 21 Fan_Pressure_CT
    (0.60, 0.80),        # 22 Fan_e_CT
    (0.95, 0.99),        # 23 SHR (UPDATED)
    (0.20, 1.10),        # 24 LGRatio
    None,                # 25 T_up (fixed)
    None,                # 26 T_lw (fixed)
    None,                # 27 dp_up (fixed)
    None,                # 28 dp_lw (fixed)
    (0.10, 0.30),        # 29 RH_up (NOW VARIABLE)
    (0.60, 0.80),        # 30 RH_lw (NOW VARIABLE)
    (-0.40, 0.0)         # 31 pcop (UPDATED)
]

assert len(params_AE_Chiller_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------------
# 3) Identify active (sampled) parameters
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
# 6) Build full vectors
# ------------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_AE_Chiller_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])

# ------------------------------------------------------
# 7) Save
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "sri_lanka" / "ae_chiller_colo_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
