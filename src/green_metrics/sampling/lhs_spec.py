"""Load LHS scenario definitions from CSV files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd

from green_metrics.paths import project_root


def _cell_empty(x: Any) -> bool:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return True
    if isinstance(x, str) and x.strip() == "":
        return True
    return False


def _parse_scalar(x: Any) -> Optional[float]:
    if _cell_empty(x):
        return None
    return float(x)


@dataclass
class LHSSpec:
    """Parsed LHS definition: base vector, active indices, bounds, sample count."""

    base: List[Optional[float]]
    active_positions: List[int]
    active_mins: np.ndarray
    active_maxs: np.ndarray
    n_samples: int
    random_seed: Optional[int]


def load_run_csv(path: Path) -> Tuple[int, Optional[int]]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    if "key" not in df.columns or "value" not in df.columns:
        raise ValueError(f"Run CSV must have columns key,value: {path}")
    kv = dict(zip(df["key"].astype(str).str.strip(), df["value"]))
    sample_count = float(kv["n_samples"])
    if not np.isfinite(sample_count) or not sample_count.is_integer() or sample_count < 1:
        raise ValueError(f"n_samples must be a positive integer: {path}")
    n_samples = int(sample_count)
    seed_raw = kv.get("random_seed", "")
    if _cell_empty(seed_raw):
        seed: Optional[int] = None
    else:
        seed = int(float(seed_raw))
    return n_samples, seed


def load_bounds_csv(
    path: Path,
) -> Tuple[List[Optional[float]], List[int], np.ndarray, np.ndarray]:
    df = pd.read_csv(path, encoding="utf-8-sig")
    required = {"index", "base", "min", "max"}
    if not required.issubset(df.columns):
        raise ValueError(f"Bounds CSV missing columns {required}: {path}")

    if len(df) < 3:
        raise ValueError(
            f"Bounds CSV must define at least three weather parameters: {path}"
        )

    indices = pd.to_numeric(df["index"], errors="raise").to_numpy(dtype=float)
    if (
        not np.isfinite(indices).all()
        or not np.equal(indices, np.floor(indices)).all()
        or (indices < 0).any()
    ):
        raise ValueError(f"Parameter indices must be non-negative integers: {path}")
    if sorted(indices.astype(int).tolist()) != list(range(len(df))):
        raise ValueError(
            f"Parameter indices must be unique, contiguous, and start at 0: {path}"
        )
    df["index"] = indices.astype(int)
    df = df.sort_values("index").reset_index(drop=True)

    max_idx = int(df["index"].max())
    base: List[Optional[float]] = [None] * (max_idx + 1)

    active_positions: List[int] = []
    mins_list: List[float] = []
    maxs_list: List[float] = []

    for _, row in df.iterrows():
        idx = int(row["index"])
        b = _parse_scalar(row["base"])
        mn = _parse_scalar(row["min"])
        mx = _parse_scalar(row["max"])
        base[idx] = b
        if mn is not None and mx is not None:
            if mn > mx:
                raise ValueError(f"Index {idx}: min must not exceed max: {path}")
            active_positions.append(idx)
            mins_list.append(mn)
            maxs_list.append(mx)
        elif mn is None and mx is None:
            continue
        else:
            raise ValueError(f"Index {idx}: min and max must both be set or both empty")

    mins = np.array(mins_list, dtype=float)
    maxs = np.array(maxs_list, dtype=float)
    return base, active_positions, mins, maxs


def load_lhs_spec(bounds_path: Path, run_path: Path) -> LHSSpec:
    base, active_positions, mins, maxs = load_bounds_csv(bounds_path)
    n_samples, seed = load_run_csv(run_path)
    return LHSSpec(
        base=base,
        active_positions=active_positions,
        active_mins=mins,
        active_maxs=maxs,
        n_samples=n_samples,
        random_seed=seed,
    )


def scenario_spec_paths(
    region: str, stem: str, root: Optional[Path] = None
) -> Tuple[Path, Path]:
    root = root or project_root()
    d = root / "config" / "lhs" / region
    return d / f"{stem}_bounds.csv", d / f"{stem}_run.csv"
