from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameter vector
# ------------------------------------------------------
params_AE_Chiller_base = [
    None, None, None,
    0.90,      # 3 UPS_e
    0.03,      # 4 PD_lr
    0.03,      # 5 L_percentage
    7.0,       # 6 delta_T_air
    700,       # 7 Fan_Pressure_CRAC
    0.70,      # 8 Fan_e_CRAC
    7000000,   # 9 Pump_Pressure_HD
    0.70,      # 10 Pump_e_HD
    4.0,       # 11 AT_CT
    0.30,      # 12 Chiller_load
    7.0,       # 13 delta_T_water
    145000,    # 14 Pump_Pressure_CW
    0.70,      # 15 Pump_e_CW
    5.0,       # 16 delta_T_CT
    200000,    # 17 Pump_Pressure_CT
    0.70,      # 18 Pump_e_CT
    0.001,     # 19 Windage_p
    6.0,       # 20 CC
    300,       # 21 Fan_Pressure_CT
    0.70,      # 22 Fan_e_CT
    0.97,      # 23 SHR
    1.0,       # 24 LGRatio
    29,        # 25 T_up
    16,        # 26 T_lw
    20,        # 27 dp_up
    -10,       # 28 dp_lw
    0.20,      # 29 RH_up
    0.70,      # 30 RH_lw
    -0.2       # 31 pcop
]

# ------------------------------------------------------
# 2) Parameter ranges
# ------------------------------------------------------
param_ranges = [
    None, None, None,

    (0.80, 0.94),        # UPS_e
    (0.02, 0.05),        # PD_lr
    (0.02, 0.05),        # L_percentage
    (5, 10),             # delta_T_air
    (400, 1000),         # Fan_Pressure_CRAC
    (0.60, 0.80),        # Fan_e_CRAC
    (6300000, 7700000),  # Pump_Pressure_HD
    (0.60, 0.80),        # Pump_e_HD
    (2.8, 6.7),          # AT_CT
    (0.1, 0.5),          # Chiller_load
    (5, 10),             # delta_T_water
    (114900, 172400),    # Pump_Pressure_CW
    (0.60, 0.80),        # Pump_e_CW
    (4, 6),              # delta_T_CT
    (166900, 250400),    # Pump_Pressure_CT
    (0.60, 0.80),        # Pump_e_CT
    (0.00005, 0.005),    # Windage_p
    (3, 12),             # CC
    (200, 400),          # Fan_Pressure_CT
    (0.60, 0.80),        # Fan_e_CT
    (0.95, 0.99),        # SHR
    (0.2, 2.0),          # LGRatio
    (27, 32),            # T_up
    (15, 18),            # T_lw
    (15, 27),            # dp_up
    (-12, -9),           # dp_lw
    (0.10, 0.30),        # RH_up
    (0.60, 0.80),        # RH_lw
    (-0.40, 0.0)         # pcop
]

assert len(params_AE_Chiller_base) == len(param_ranges)

# ------------------------------------------------------
# 3) Extract active variables
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
# 7) Save CSV
# ------------------------------------------------------

# Gets the absolute path to the 'green-metrics' folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "usa" / "usa_ae_chiller_colo_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
