"""Create the starting files for a new region / dataset."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Optional

from green_metrics.batch.registry import SCENARIOS, ScenarioConfig
from green_metrics.paths import project_root


def init_scenario(
    name: str, template: str, root: Optional[Path] = None
) -> Path:
    """Copy a built-in scenario's bounds/run CSVs and write a scenario JSON.

    Creates ``config/lhs/<name>/``, ``data/epw_files/<name>/`` and
    ``config/scenarios/<name>.json``. Returns the JSON path.
    """
    if template not in SCENARIOS:
        raise ValueError(f"Unknown template {template!r}; choose from {sorted(SCENARIOS)}")
    base: ScenarioConfig = SCENARIOS[template]
    root = Path(root) if root else project_root()
    src_dir = project_root() / "config" / "lhs" / base.region
    dst_dir = root / "config" / "lhs" / name
    dst_dir.mkdir(parents=True, exist_ok=True)
    for kind in ("bounds", "run"):
        src = src_dir / f"{base.bounds_stem}_{kind}.csv"
        dst = dst_dir / f"{base.bounds_stem}_{kind}.csv"
        if not dst.exists():
            shutil.copyfile(src, dst)
    (root / "data" / "epw_files" / name).mkdir(parents=True, exist_ok=True)

    cfg = {
        "region": name,
        "bounds_file": f"config/lhs/{name}/{base.bounds_stem}_bounds.csv",
        "run_file": f"config/lhs/{name}/{base.bounds_stem}_run.csv",
        "samples_file": f"data/lhs_samples/{name}/{base.bounds_stem}_samples.csv",
        "weather_dir": f"data/epw_files/{name}",
        "output_dir": f"output/{name}",
        "model_dir": "data/pkl_files",
        "sim_func": base.sim_func,
        "sheet_prefix": base.sheet_prefix,
        "pue_column": base.pue_column,
        "wue_column": base.wue_column,
    }
    out = root / "config" / "scenarios" / f"{name}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise FileExistsError(f"{out} already exists")
    out.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    return out
