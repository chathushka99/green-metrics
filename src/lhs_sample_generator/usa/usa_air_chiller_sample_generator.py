from pathlib import Path

import numpy as np
import lhsmdu
import pandas as pd

# ------------------------------------------------------
# 1) Base parameters (only vector structure matters)
# ------------------------------------------------------
params_AIRChiller_base = [
    None, None, None,
    0.86,      # 3 UPS_e
    0.03,      # 4 PD_lr
    0.03,      # 5 L_percentage
    0.97,      # 6 SHR
    7.0,       # 7 delta_T_air
    600,       # 8 Fan_Pressure_CRAC
    0.70,      # 9 Fan_e_CRAC
    7000000,   # 10 Pump_Pressure_HD
    0.70,      # 11 Pump_e_HD
    0.70,      # 12 HTE
    7.0,       # 13 delta_T_water
    150000,    # 14 Pump_Pressure_CW
    0.70,      # 15 Pump_e_CW
    0.30,      # 16 Chiller_load
    0.0,       # 17 pcop
    29,        # 18 T_up
    16,        # 19 T_lw
    20,        # 20 dp_up
    -10,       # 21 dp_lw
    0.20,      # 22 RH_up
    0.70       # 23 RH_lw
]

# ------------------------------------------------------
# 2) Parameter ranges (from your table)
# ------------------------------------------------------
param_ranges = [
    None, None, None,

    (0.80, 0.94),          # UPS_e
    (0.02, 0.05),          # PD_lr
    (0.02, 0.05),          # L_percentage
    (0.95, 0.99),          # SHR
    (5, 10),               # delta_T_air
    (400, 900),            # Fan_Pressure_CRAC
    (0.60, 0.80),          # Fan_e_CRAC
    (6300000, 7700000),    # Pump_Pressure_HD
    (0.60, 0.80),          # Pump_e_HD
    (0.65, 0.80),          # HTE
    (5, 10),               # delta_T_water
    (114900, 172400),      # Pump_Pressure_CW
    (0.60, 0.80),          # Pump_e_CW
    (0.1, 0.5),            # Chiller_load
    (-0.40, 0.25),         # pcop
    (27, 32),              # T_up
    (15, 18),              # T_lw
    (15, 27),              # dp_up
    (-12, -9),             # dp_lw
    (0.10, 0.30),          # RH_up
    (0.60, 0.80)           # RH_lw
]

assert len(params_AIRChiller_base) == len(param_ranges)

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
# 4) Generate LHS samples
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

# Gets the absolute path to the 'green-metrics' folder
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
output_path = BASE_DIR / "lhs_samples" / "usa" / "usa_air_chiller_samples.csv"
output_path.parent.mkdir(parents=True, exist_ok=True)

df_samples = pd.DataFrame(all_samples)
df_samples.to_csv(output_path, index=False)

print(f"Saved: {output_path}")
