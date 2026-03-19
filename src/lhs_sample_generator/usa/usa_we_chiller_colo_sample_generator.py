from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# -----------------------------------------------------------
# 1) Base parameter vector (length must match ranges)
# -----------------------------------------------------------
params_Chiller_base = [
    None, None, None,
    0.90,      # 3 UPS_e
    0.03,      # 4 PD_lr
    0.03,      # 5 L_percentage
    0.97,      # 6 SHR
    7.0,       # 7 delta_T_air
    600,       # 8 Fan_Pressure_CRAC
    0.70,      # 9 Fan_e_CRAC
    7000000,   # 10 Pump_Pressure_HD
    0.70,      # 11 Pump_e_HD
    0.75,      # 12 HTE
    7.0,       # 13 delta_T_water
    4.0,       # 14 AT_CT
    2.2,       # 15 AT_HE
    145000,    # 16 Pump_Pressure_WE
    0.70,      # 17 Pump_e_WE
    145000,    # 18 Pump_Pressure_CW
    0.70,      # 19 Pump_e_CW
    0.30,      # 20 Chiller_load
    5.0,       # 21 delta_T_CT
    200000,    # 22 Pump_Pressure_CT
    0.70,      # 23 Pump_e_CT
    0.001,     # 24 Windage_p
    6.0,       # 25 CC
    1.0,       # 26 LGRatio
    300,       # 27 Fan_Pressure_CT
    0.70,      # 28 Fan_e_CT
    29,        # 29 T_up
    16,        # 30 T_lw
    20,        # 31 dp_up
    -10,       # 32 dp_lw
    0.20,      # 33 RH_up
    0.70,      # 34 RH_lw
    -0.2       # 35 pcop
]

# -----------------------------------------------------------
# 2) Parameter ranges from your table
# -----------------------------------------------------------
param_ranges = [
    None, None, None,

    (0.80, 0.94),        # UPS_e
    (0.02, 0.05),        # PD_lr
    (0.02, 0.05),        # L_percentage
    (0.95, 0.99),        # SHR
    (5, 10),             # delta_T_air
    (400, 900),          # Fan_Pressure_CRAC
    (0.60, 0.80),        # Fan_e_CRAC
    (6300000, 7700000),  # Pump_Pressure_HD
    (0.60, 0.80),        # Pump_e_HD
    (0.65, 0.90),        # HTE
    (5, 10),             # delta_T_water
    (2.8, 6.7),          # AT_CT
    (1.7, 2.8),          # AT_HE
    (114900, 172400),    # Pump_Pressure_WE
    (0.60, 0.80),        # Pump_e_WE
    (114900, 172400),    # Pump_Pressure_CW
    (0.60, 0.80),        # Pump_e_CW
    (0.1, 0.5),          # Chiller_load
    (4, 6),              # delta_T_CT
    (166900, 250400),    # Pump_Pressure_CT
    (0.60, 0.80),        # Pump_e_CT
    (0.00005, 0.005),    # Windage_p
    (3, 12),             # CC
    (0.2, 2.0),          # LGRatio
    (200, 400),          # Fan_Pressure_CT
    (0.60, 0.80),        # Fan_e_CT
    (27, 32),            # T_up
    (15, 18),            # T_lw
    (15, 27),            # dp_up
    (-12, -9),           # dp_lw
    (0.10, 0.30),        # RH_up
    (0.60, 0.80),        # RH_lw
    (-0.40, 0.0)         # pcop
]

assert len(params_Chiller_base) == len(param_ranges)

# -----------------------------------------------------------
# 3) Identify sampled parameters
# -----------------------------------------------------------
active_ranges = []
active_positions = []

for i, r in enumerate(param_ranges):
    if isinstance(r, tuple):
        active_ranges.append(r)
        active_positions.append(i)

n_vars = len(active_ranges)
n_samples = 50

# -----------------------------------------------------------
# 4) Latin Hypercube Sampling
# -----------------------------------------------------------
unit_samples = np.array(lhsmdu.sample(n_vars, n_samples)).T

# -----------------------------------------------------------
# 5) Scale to actual ranges
# -----------------------------------------------------------
mins = np.array([r[0] for r in active_ranges])
maxs = np.array([r[1] for r in active_ranges])
scaled = mins + (maxs - mins) * unit_samples

# -----------------------------------------------------------
# 6) Build full sample vectors
# -----------------------------------------------------------
all_samples = []

for i in range(n_samples):
    sample = params_Chiller_base.copy()
    for j, idx in enumerate(active_positions):
        sample[idx] = scaled[i, j]
    all_samples.append(sample)

all_samples = np.array(all_samples)

print("Generated samples shape:", all_samples.shape)
print(all_samples[:3])

# Gets the absolute path to the 'green-metrics' folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "usa" / "usa_we_chiller_colo_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")