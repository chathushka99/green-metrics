"""Batch EPW simulation across districts and LHS samples."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

import green_metrics.simulation.dc as sim_dc
from green_metrics.batch.registry import load_scenario, resolve_path
from green_metrics.paths import project_root


WEATHER_SUFFIXES = (".epw", ".csv")


def read_epw(filepath: Path) -> pd.DataFrame:
    """Read an EnergyPlus weather file: dry-bulb (C), RH (%), pressure (Pa)."""
    df = pd.read_csv(filepath, skiprows=8, header=None)
    df = df.iloc[:, [6, 8, 9]]
    df.columns = ["T_oa", "RH_oa", "P_oa"]
    return df


def read_weather_csv(filepath: Path) -> pd.DataFrame:
    """Read a generic hourly CSV with columns T_oa (C), RH_oa (%), P_oa (Pa)."""
    df = pd.read_csv(filepath, encoding="utf-8-sig")
    df.columns = [str(c).strip() for c in df.columns]
    missing = {"T_oa", "RH_oa", "P_oa"}.difference(df.columns)
    if missing:
        raise ValueError(f"{filepath} is missing columns: {', '.join(sorted(missing))}")
    return df[["T_oa", "RH_oa", "P_oa"]].astype(float)


def read_weather(filepath: Path) -> pd.DataFrame:
    if filepath.suffix.lower() == ".epw":
        return read_epw(filepath)
    return read_weather_csv(filepath)


def simulate_sample(
    fn,
    weather_df: pd.DataFrame,
    sample: pd.Series,
    pue_column: str = "PUE",
    wue_column: str = "WUE",
    desc: Optional[str] = None,
) -> pd.DataFrame:
    """Run one parameter sample through ``fn`` for every weather row."""
    params = sample.values.tolist()
    results = []
    for hour, t_oa, rh_oa, p_oa in tqdm(
        weather_df[["T_oa", "RH_oa", "P_oa"]].itertuples(index=True, name=None),
        total=len(weather_df),
        desc=desc,
        unit="hour",
        disable=desc is None,
    ):
        params[0], params[1], params[2] = t_oa, rh_oa, p_oa
        pue, wue = fn(params)[:2]
        results.append([hour, t_oa, rh_oa, p_oa, pue, wue])
    return pd.DataFrame(
        results,
        columns=["Hour", "T_oa (°C)", "RH_oa (%)", "P_oa (Pa)", pue_column, wue_column],
    )


def run_scenario(
    scenario_id: Optional[str] = None,
    config_file: Optional[Path] = None,
    root: Optional[Path] = None,
    overwrite: bool = False,
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
        if path.is_file() and path.suffix.lower() in WEATHER_SUFFIXES
    )
    if not epw_files:
        raise ValueError(f"No .epw or .csv weather files found in: {epw_dir}")
    for epw_path in epw_files:
        district = epw_path.stem
        output_path = out_dir / f"{district}.xlsx"
        if output_path.exists() and not overwrite:
            print(f"SKIP: {district} (output exists; use --overwrite to redo)")
            continue
        print(f"RUN: {district}")
        weather_df = read_weather(epw_path)
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for idx, sample in samples.iterrows():
                df_out = simulate_sample(
                    fn, weather_df, sample, cfg.pue_column, cfg.wue_column,
                    desc=f"{cfg.sheet_prefix} sample {idx + 1}",
                )
                sheet_name = f"{cfg.sheet_prefix}_{idx + 1}"
                df_out.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Saved: {output_path}")
    print("Done.")
