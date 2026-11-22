# green-metrics

`green-metrics` calculates hourly data-center Power Usage Effectiveness (PUE)
and Water Usage Effectiveness (WUE) for EPW weather data. It generates Latin
Hypercube Sampling (LHS) parameter sets and runs the selected cooling-system
model for every EPW file in a configured folder.

The project uses a `src/` package layout and a command-line interface. The
included Sri Lanka and USA scenarios remain available, and custom scenarios
can point to different EPW locations, parameter bounds, output folders, and
COP model directories without editing Python code.

## Quick start

Requires **Python 3.10 - 3.13** (developed on 3.12). Step-by-step instructions, including installing
Python and creating the virtual environment, are in **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)**.

```powershell
uv venv --python 3.12 .venv               # or: py -3.12 -m venv .venv
uv pip install -r requirements.txt -e .   # or: pip install -r requirements.txt -e .
python -m green_metrics list
python -m green_metrics sample   --scenario usa_dx
python -m green_metrics simulate --scenario usa_dx
```

`run_green_metrics.bat` / `run_green_metrics.sh` do setup + sample + simulate in one go.
A notebook version lives in `notebooks/green_metrics.ipynb`.

### Dependencies

`requirements.txt` holds compatible ranges, `requirements-lock.txt` the exact tested versions and
`requirements-notebook.txt` adds Jupyter. The legacy pins (Python 3.7, scikit-learn 0.22) are no longer
needed: the Gaussian-process `.pkl` models load through a small compatibility shim, and
`tests/check_models.py` confirms predictions match scikit-learn 0.22.2 to about 1e-12. Do not load
pickle files from untrusted sources.

## Project layout

| Path | Purpose |
| --- | --- |
| `config/lhs/<region>/` | LHS parameter bounds and sample-count CSVs |
| `config/scenarios/` | Scenario JSONs created by `init` |
| `notebooks/` | Jupyter notebook version |
| `docs/SETUP_GUIDE.md` | Python + venv installation guide |
| `tests/` | Model compatibility check |
| `data/epw_files/<region>/` | EPW weather inputs |
| `data/lhs_samples/<region>/` | Generated sample matrices |
| `data/pkl_files/` | Gaussian-process COP model pickles |
| `output/<region>/` | Excel outputs, one workbook per EPW location |
| `src/green_metrics/` | Installable package and CLI |

The simulation uses weather data columns 6, 8, and 9 from each EPW file for
outdoor dry-bulb temperature (°C), relative humidity (%), and pressure (Pa).
Inputs therefore need to be valid EPW files with the expected EPW column
layout.

The COP models used by the simulation are `COP_2.pkl` (water-cooled chiller),
`COP_DX.pkl` (DX), and `COP_AC.pkl` (air-cooled chiller). Place compatible
models in `data/pkl_files/` or configure another `model_dir` in a custom
scenario.

## Run an included scenario

Built-in scenarios (`python -m green_metrics list`) are `<region>_<model>` for region in `sri_lanka`, `usa`
and model in `dx`, `air_chiller`, `chiller`, `we_chiller_colo`, `ae_chiller_colo`.

1. Review the bounds/run CSVs in `config/lhs/<region>/`. Bounds columns: `index,base,min,max,name`;
   indices start at 0 and are contiguous; positions 0-2 are filled with weather temperature, humidity and
   pressure. Set both `min` and `max` to vary a parameter, or leave both empty to use `base`.
2. `python -m green_metrics sample --scenario usa_dx`
3. `python -m green_metrics simulate --scenario usa_dx [--overwrite]`
4. Results: one workbook per weather file in `output/<region>/`, one sheet per sample. Existing
   workbooks are skipped unless `--overwrite` is given.

## Use your own data

```powershell
python -m green_metrics init mysite --template usa_chiller
```

creates `config/lhs/mysite/`, `data/epw_files/mysite/` and `config/scenarios/mysite.json`. Drop in weather
files (`.epw`, or `.csv` with `T_oa`, `RH_oa`, `P_oa` columns), edit the bounds CSV, then run `sample` and
`simulate` with `--config config/scenarios/mysite.json` (add `--root` if the data lives elsewhere).
Scenario JSON keys: `region, bounds_file, run_file, samples_file, weather_dir, output_dir, model_dir,
sim_func, sheet_prefix, pue_column, wue_column`; paths may be absolute or relative to `--root`.

Parameters are consumed positionally by the chosen `sim_func` (`PUE_WUE_DX`, `PUE_WUE_AIRChiller`,
`PUE_WUE_Chiller`, `PUE_WUE_WE_Chiller_Colo`, `PUE_WUE_AE_Chiller_Colo`), so keep the bounds CSV order of
the template. To add a cooling model, implement a `PUE_WUE_*` function returning `(PUE, WUE)` in
`green_metrics/simulation/dc.py`.

## Attribution

This project builds on
[Data-Center-Water-footprint](https://github.com/nuoaleon/Data-Center-Water-footprint);
credit to @nuoaleon.
