"""Batch EPW simulation across districts and LHS samples."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

import green_metrics.simulation.dc as sim_dc
from green_metrics.batch.registry import load_scenario, resolve_path
from green_metrics.paths import project_root


def read_epw(filepath: Path) -> pd.DataFrame:
    df = pd.read_csv(filepath, skiprows=8, header=None)
    df = df.iloc[:, [6, 8, 9]]
    df.columns = ["T_oa", "RH_oa", "P_oa"]
    return df


def run_scenario(
    scenario_id: Optional[str] = None,
    config_file: Optional[Path] = None,
    root: Optional[Path] = None,
) -> None:
    cfg = load_scenario(scenario_id, config_file)
    root = root or project_root()
    epw_dir = (
        resolve_path(root, cfg.weather_dir)
        if cfg.weather_dir
        else root / "data" / "epw_files" / cfg.region
    )
    out_dir = (
        resolve_path(root, cfg.output_dir)
        if cfg.output_dir
        else root / "output" / cfg.region
    )
    samples_path = (
        resolve_path(root, cfg.samples_file)
        if cfg.samples_file
        else root / "data" / "lhs_samples" / cfg.region / cfg.samples_csv
    )
    if not samples_path.is_file():
        raise FileNotFoundError(f"Sample CSV not found: {samples_path}")
    if not epw_dir.is_dir():
        raise FileNotFoundError(f"EPW directory not found: {epw_dir}")
    model_dir = (
        resolve_path(root, cfg.model_dir)
        if cfg.model_dir
        else root / "data" / "pkl_files"
    )
    sim_dc.configure_model_directory(model_dir)
    fn = getattr(sim_dc, cfg.sim_func, None)
    if not callable(fn) or not cfg.sim_func.startswith("PUE_WUE_"):
        raise ValueError(f"Unknown simulation function: {cfg.sim_func}")
    samples = pd.read_csv(samples_path)
    if samples.empty or len(samples.columns) < 3:
        raise ValueError(
            "Sample CSV must contain at least one row and three weather parameter columns: "
            f"{samples_path}"
        )
    out_dir.mkdir(parents=True, exist_ok=True)

    epw_files = sorted(
        path
        for path in epw_dir.iterdir()
        if path.is_file() and path.suffix.lower() == ".epw"
    )
    if not epw_files:
        raise ValueError(f"No .epw files found in: {epw_dir}")
    for epw_path in epw_files:
        district = epw_path.stem
        output_path = out_dir / f"{district}.xlsx"
        if output_path.exists():
            print(f"SKIP: {district} (output exists)")
            continue
        print(f"RUN: {district}")
        weather_df = read_epw(epw_path)
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for idx, sample in samples.iterrows():
                results = []
                desc = f"{cfg.sheet_prefix} sample {idx + 1}"
                for row in tqdm(
                    weather_df.itertuples(index=True),
                    total=len(weather_df),
                    desc=desc,
                    unit="hour",
                ):
                    hour = row.Index
                    t_oa = row.T_oa
                    rh_oa = row.RH_oa
                    p_oa = row.P_oa
                    p = sample.values.tolist()
                    p[0], p[1], p[2] = t_oa, rh_oa, p_oa
                    res = fn(p)
                    results.append([hour, t_oa, rh_oa, p_oa, res[0], res[1]])
                df_out = pd.DataFrame(
                    results,
                    columns=[
                        "Hour",
                        "T_oa (°C)",
                        "RH_oa (%)",
                        "P_oa (Pa)",
                        cfg.pue_column,
                        cfg.wue_column,
                    ],
                )
                sheet_name = f"{cfg.sheet_prefix}_{idx + 1}"
                df_out.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Saved: {output_path}")
    print("Done.")
