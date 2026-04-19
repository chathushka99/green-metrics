# green-metrics

Hourly **PUE** (Power Usage Effectiveness) and **WUE** (Water Usage Effectiveness) models for data-center cooling scenarios, driven by **EPW** weather files. Latin Hypercube samples define equipment and operating parameters; each run writes multi-sheet Excel results per weather location.

## Layout

| Path | Purpose |
|------|---------|
| `config/lhs/<region>/` | LHS definitions: `<stem>_bounds.csv` (index, base, min, max, name) and `<stem>_run.csv` (`n_samples`, optional `random_seed`) |
| `data/epw_files/<region>/` | Input `.epw` weather files |
| `data/lhs_samples/<region>/` | Generated parameter CSVs consumed by simulations |
| `data/pkl_files/` | Gaussian-process COP models (`COP_2.pkl`, `COP_DX.pkl`, `COP_AC.pkl`) — **not included** in the repository; add locally |
| `output/<region>/` | Excel outputs (`<district>.xlsx`) |
| `src/green_metrics/` | Installable package (simulation, batch runner, LHS helpers) |

## Setup

Requires Python 3.8+. From the repository root:

```text
pip install -e .
```

Use a virtual environment if you prefer. Dependencies are listed in `pyproject.toml` (legacy pins remain in `requirements.txt` for reference).

## Gaussian-process models

Place these pickle files under `data/pkl_files/`:

- `COP_2.pkl` — water-cooled chiller COP model  
- `COP_DX.pkl` — DX COP model  
- `COP_AC.pkl` — air-cooled chiller COP model  

Models load **on first use** inside the simulation functions so importing the package succeeds without them; running a scenario that needs a missing file raises `FileNotFoundError` with the expected path.

## Workflow

1. **Adjust LHS definitions** (optional): edit CSVs under `config/lhs/<region>/`.

2. **Generate sample matrices** for a scenario:

   ```text
   python -m green_metrics sample --scenario sri_lanka_dx
   ```

   Scenario ids combine region and plant type, for example: `sri_lanka_chiller`, `usa_we_chiller_colo`, `usa_ae_chiller_colo`. All valid ids appear in `--help`.

3. **Run simulations** over every `.epw` in the matching region folder:

   ```text
   python -m green_metrics simulate --scenario sri_lanka_dx
   ```

   Existing output files are skipped (same district filename under `output/<region>/`).

4. **CLI entry point** (after install):

   ```text
   green-metrics sample --scenario usa_chiller
   green-metrics simulate --scenario usa_chiller
   ```

Legacy scripts under `src/pue_wue_scripts/` and `src/lhs_sample_generator/` delegate to the same commands.

## Scenario ids

**Sri Lanka:** `sri_lanka_dx`, `sri_lanka_air_chiller`, `sri_lanka_chiller`, `sri_lanka_we_chiller_colo`, `sri_lanka_ae_chiller_colo`

**USA:** `usa_dx`, `usa_air_chiller`, `usa_chiller`, `usa_we_chiller_colo`, `usa_ae_chiller_colo`

## Implementation notes

- Project root is resolved by locating `pyproject.toml`; use `pip install -e .` from the clone so paths resolve correctly.
- Simulation code lives in `green_metrics.simulation.dc`. Imports such as `simulation_functions.simulation_funs_dc` use a thin shim under `src/simulation_functions/` for compatibility.
