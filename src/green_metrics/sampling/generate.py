"""Latin Hypercube sample generation from CSV specs."""

from pathlib import Path
from typing import Optional

import lhsmdu
import numpy as np
import pandas as pd

from green_metrics.batch.registry import SCENARIOS, load_scenario, resolve_path
from green_metrics.paths import project_root
from green_metrics.sampling.lhs_spec import LHSSpec, load_lhs_spec, scenario_spec_paths


def generate_lhs_rows(spec: LHSSpec):
    if spec.random_seed is not None:
        np.random.seed(spec.random_seed)
    n_vars = len(spec.active_positions)
    if n_vars == 0:
        raise ValueError("LHS spec has no varying parameters")
    unit_samples = np.array(lhsmdu.sample(n_vars, spec.n_samples)).T
    scaled = spec.active_mins + (spec.active_maxs - spec.active_mins) * unit_samples
    rows = []
    for i in range(spec.n_samples):
        vec = list(spec.base)
        for j, pos in enumerate(spec.active_positions):
            vec[pos] = scaled[i, j]
        rows.append(vec)
    return rows


def write_samples_for_scenario(
    scenario_id: Optional[str] = None,
    config_file: Optional[Path] = None,
    root: Optional[Path] = None,
) -> Path:
    cfg = load_scenario(scenario_id, config_file)
    root = root or project_root()
    if cfg.bounds_file and cfg.run_file:
        bounds_path = resolve_path(root, cfg.bounds_file)
        run_path = resolve_path(root, cfg.run_file)
    else:
        bounds_path, run_path = scenario_spec_paths(cfg.region, cfg.bounds_stem, root)
    spec = load_lhs_spec(bounds_path, run_path)
    rows = generate_lhs_rows(spec)
    out = (
        resolve_path(root, cfg.samples_file)
        if cfg.samples_file
        else root / "data" / "lhs_samples" / cfg.region / cfg.samples_csv
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    return out