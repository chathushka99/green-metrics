import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from simulation_functions.simulation_funs_dc import PUE_WUE_AIRChiller

# ------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------
EPW_FOLDER = BASE_DIR / "data" / "epw_files" / "sri_lanka"
OUTPUT_FOLDER = BASE_DIR / "output" / "sri_lanka"
SAMPLES_FOLDER = BASE_DIR / "data" / "lhs_samples" / "sri_lanka"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------------------------------------------------------
# IMPORT SAMPLE FILES
# ------------------------------------------------------------------
ac_samples = pd.read_csv(os.path.join(SAMPLES_FOLDER, "air_chiller_samples.csv"))


# ------------------------------------------------------------------
# EPW READER
# ------------------------------------------------------------------
def read_epw(filepath):
    df = pd.read_csv(filepath, skiprows=8, header=None)
    df = df.iloc[:, [6, 8, 9]]
    df.columns = ["T_oa", "RH_oa", "P_oa"]
    return df


# ------------------------------------------------------------------
# MAIN LOOP (PER DISTRICT FILE)
# ------------------------------------------------------------------
for epw_file in os.listdir(EPW_FOLDER):
    if not epw_file.lower().endswith(".epw"):
        continue

    district = os.path.splitext(epw_file)[0]
    output_path = os.path.join(OUTPUT_FOLDER, f"{district}.xlsx")

    # Skip if already simulated
    if os.path.exists(output_path):
        print(f"⏭ Skipping {district} (already exists)")
        continue

    print(f"\n▶ Running district: {district}")
    weather_df = read_epw(os.path.join(EPW_FOLDER, epw_file))

    # Create writer to save multiple sheets
    writer = pd.ExcelWriter(output_path, engine="openpyxl")

    # ------------------------------------------------------------------
    # RUN FOR EACH AIR CHILLER SAMPLE
    # ------------------------------------------------------------------
    for idx, sample in ac_samples.iterrows():
        results = []
        for row in tqdm(weather_df.itertuples(index=True),
                        total=len(weather_df),
                        desc=f"AIRChiller Sample {idx + 1}",
                        unit="hour"):
            hour = row.Index
            T_oa = row.T_oa
            RH_oa = row.RH_oa
            P_oa = row.P_oa

            p = sample.values.tolist()
            p[0], p[1], p[2] = T_oa, RH_oa, P_oa

            res = PUE_WUE_AIRChiller(p)
            results.append([hour, T_oa, RH_oa, P_oa, res[0], res[1]])

        df_out = pd.DataFrame(results, columns=[
            "Hour", "T_oa (°C)", "RH_oa (%)", "P_oa (Pa)",
            "PUE_AIRChiller", "WUE_AIRChiller"
        ])
        df_out.to_excel(writer, sheet_name=f"AIRChiller_{idx + 1}", index=False)

    # ------------------------------------------------------------------
    # SAVE
    # ------------------------------------------------------------------
    print(f"✔ Saved: {output_path}")

print("\n✅ All completed districts with samples!")
