import os
import sys
from pathlib import Path

import pandas as pd
from tqdm import tqdm

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SRC_DIR = BASE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from simulation_functions.simulation_funs_dc import PUE_WUE_AE_Chiller_Colo

# ------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------
EPW_FOLDER = BASE_DIR / "data" / "epw_files" / "usa"
OUTPUT_FOLDER = BASE_DIR / "output" / "usa"
SAMPLES_FOLDER = BASE_DIR / "data" / "lhs_samples" / "usa"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ------------------------------------------------------------------
# IMPORT SAMPLE FILES
# ------------------------------------------------------------------
ae_chiller_samples = pd.read_csv(os.path.join(SAMPLES_FOLDER, "usa_ae_chiller_colo_samples.csv"))


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

    sheets_written = 0

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # ------------------------------------------------------------------
        # RUN FOR EACH AE CHILLER SAMPLE (example)
        # ------------------------------------------------------------------
        for idx, sample in ae_chiller_samples.iterrows():
            results = []
            desc = f"AE Chiller Colo Sample {idx + 1}"
            for row in tqdm(weather_df.itertuples(index=True),
                            total=len(weather_df),
                            desc=desc,
                            unit="hour"):
                hour = row.Index
                T_oa = row.T_oa
                RH_oa = row.RH_oa
                P_oa = row.P_oa

                p = sample.values.tolist()
                p[0], p[1], p[2] = T_oa, RH_oa, P_oa

                res = PUE_WUE_AE_Chiller_Colo(p)
                results.append([hour, T_oa, RH_oa, P_oa, res[0], res[1]])

            df_out = pd.DataFrame(results, columns=[
                "Hour", "T_oa (°C)", "RH_oa (%)", "P_oa (Pa)",
                "PUE_AE_Chiller", "WUE_AE_Chiller"
            ])
            sheet_name = f"AE_Chiller_{idx + 1}"

            df_out.to_excel(writer, sheet_name=sheet_name, index=False)
            sheets_written += 1

    if sheets_written > 0:
        print(f"✔ Saved: {output_path}")
    else:
        # Remove the file if nothing was written
        if os.path.exists(output_path):
            os.remove(output_path)
        print(f"⚠ Nothing to save for {district}, file removed.")

print("\n✅ All completed districts with samples!")
