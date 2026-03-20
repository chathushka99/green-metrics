from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameter vector (length & fixed defaults)
# ------------------------------------------------------
params_WE_Chiller_base = [
    None, None, None,
    0.92,     # 3 UPS_e
    0.035,    # 4 PD_lr
    0.035,    # 5 L_percentage
    0.95,     # 6 SHR
    10.0,     # 7 delta_T_air
    800,      # 8 Fan_Pressure_CRAC
    0.70,     # 9 Fan_e_CRAC
    6500,     # 10 Pump_Pressure_HD
    0.70,     # 11 Pump_e_HD
    0.78,     # 12 HTE
    11.0,     # 13 delta_T_water
    4.5,      # 14 AT_CT
    2.2,      # 15 AT_HE
    145000,   # 16 Pump_Pressure_WE
    0.70,     # 17 Pump_e_WE
    145000,   # 18 Pump_Pressure_CW
    0.70,     # 19 Pump_e_CW
    0.30,     # 20 Chiller_load
    9.0,      # 21 delta_T_CT
    300,      # 22 Pump_Pressure_CT
    0.83,     # 23 Pump_e_CT
    0.001,    # 24 Windage_p
    5.0,      # 25 CC
    0.6,      # 26 LGRatio
    300,      # 27 Fan_Pressure_CT
    0.83,     # 28 Fan_e_CT
    27,       # 29 T_up (fixed)
    18,       # 30 T_lw (fixed)
    15,       # 31 dp_up (fixed)
    -9,       # 32 dp_lw (fixed)
    70,       # 33 RH_up (fixed)
    8,        # 34 RH_lw (fixed)
    -20       # 35 pcop
]

# ------------------------------------------------------
# 2) Parameter ranges (None = fixed)
# ------------------------------------------------------
param_ranges = [
    None, None, None,
    (0.90, 0.95),            # 3 UPS_e
    (0.02, 0.05),            # 4 PD_lr
    (0.02, 0.05),            # 5 L_percentage
    (0.90, 1.00),            # 6 SHR
    (8.0, 12.0),             # 7 delta_T_air
    (300, 1200),             # 8 Fan_Pressure_CRAC
    (0.60, 0.80),            # 9 Fan_e_CRAC
    (6000, 7000),            # 10 Pump_Pressure_HD
    (0.60, 0.80),            # 11 Pump_e_HD
    (0.65, 0.90),            # 12 HTE
    (10.0, 12.0),            # 13 delta_T_water
    (3.0, 6.0),              # 14 AT_CT
    (1.7, 2.8),              # 15 AT_HE
    (114900, 172400),        # 16 Pump_Pressure_WE
    (0.60, 0.80),            # 17 Pump_e_WE
    (114900, 172400),        # 18 Pump_Pressure_CW
    (0.60, 0.80),            # 19 Pump_e_CW
    (0.10, 0.50),            # 20 Chiller_load
    (5.0, 13.0),             # 21 delta_T_CT
    (200, 400),              # 22 Pump_Pressure_CT
    (0.78, 0.88),            # 23 Pump_e_CT
    (0.000005, 0.003),       # 24 Windage_p
    (3.0, 7.0),              # 25 CC
    (0.20, 1.10),            # 26 LGRatio
    (200, 400),              # 27 Fan_Pressure_CT
    (0.78, 0.88),            # 28 Fan_e_CT
    None,                    # 29 fixed
    None,                    # 30 fixed
    None,                    # 31 fixed
    None,                    # 32 fixed
    None,                    # 33 fixed
    None,                    # 34 fixed
    (-40.0, 0.0)             # 35 pcop
]

assert len(params_WE_Chiller_base) == len(param_ranges), "Length mismatch!"

# ------------------------------------------------------
# 3) Extract active parameters
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
# 6) Assemble full vectors
# ------------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_WE_Chiller_base.copy()
    for j, pos in enumerate(active_positions):
        sample[pos] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])

# ------------------------------------------------------
# 7) Save to CSV
# ------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "sri_lanka" / "chiller_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
