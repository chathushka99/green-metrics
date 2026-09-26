# green-metrics

`green-metrics` calculates hourly data-center Power Usage Effectiveness (PUE)
and Water Usage Effectiveness (WUE) for EPW weather data. It generates Latin
Hypercube Sampling (LHS) parameter sets and runs the selected cooling-system
model for every EPW file in a configured folder.

The project uses a `src/` package layout and a command-line interface. The
included Sri Lanka and USA scenarios remain available, and custom scenarios
can point to different EPW locations, parameter bounds, output folders, and
COP model directories without editing Python code.

## Python and pickle compatibility

Use **CPython 3.7.9** for the included legacy Gaussian-process pickle models.
Pickle files do not carry a portable model format: loading depends on the
Python and library versions present when they were created, particularly
scikit-learn. The repository's legacy dependency pins are the best compatibility
baseline; if your `.pkl` files were created with another scikit-learn/Python
stack, use that exact stack instead. Do not load pickle files from untrusted
sources.

Python 3.7 is end-of-life. Keep this environment isolated and do not expose it
to untrusted input or networks. For production use, retrain/export the models
into a supported serialization format and update the runtime dependencies.

### Install Python 3.7

Use **CPython 3.7.9**. Download it from
[python.org](https://www.python.org/downloads/release/python-379/). On Windows,
include the Python Launcher during installation. On macOS/Linux, make sure the
interpreter is available as `python3.7`.

### Windows

Open PowerShell in the project directory and create an isolated environment:

```powershell
py -3.7 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade "pip<24.1"
python -m pip install -e .
```

You can also run the complete setup, sample generation, and simulation flow
with the supplied scripts. `run_green_metrics.bat` calls the PowerShell runner;
if Python 3.7 is missing, the script opens the Python 3.7.9 download page.
Install Python and rerun the command:

```powershell
.\run_green_metrics.bat
.\run_green_metrics.bat -Scenario usa_chiller
```

The script creates `.venv` with Python 3.7, installs the pinned dependencies
and this package, generates LHS samples, then simulates all EPW files for the
selected scenario. Results are written to that scenario's configured output
directory. It defaults to `sri_lanka_dx`.

For custom data, provide a scenario JSON file instead:

```powershell
.\run_green_metrics.bat -Config config\my_scenario.json
```

Use `-Root C:\path\to\project-data` when the configuration and data are not
under the project directory. Paths in the scenario JSON are resolved from that
root. The script never replaces an existing `.venv`; if it was created with a
different Python version, rename or remove that environment before rerunning.

### macOS and Linux

From a terminal at the project root, make the shell script executable and run
it. The script creates `.venv`, installs pinned dependencies, generates
samples, and runs the simulations:

```sh
chmod +x run_green_metrics.sh
./run_green_metrics.sh
./run_green_metrics.sh --scenario usa_chiller
```

To use a custom scenario:

```sh
./run_green_metrics.sh --config config/my_scenario.json
./run_green_metrics.sh --config config/my_scenario.json --root /path/to/data-root
```

If `python3.7` is missing, install CPython 3.7.9 and rerun the script. Like the
Windows script, it does not replace an existing `.venv` created with another
Python version. Rename or remove that environment before rerunning. The pinned
dependencies in `pyproject.toml` correspond to `requirements.txt`.

Check the command options with:

```text
python -m green_metrics --help
python -m green_metrics sample --help
python -m green_metrics simulate --help
```

## Project layout

| Path | Purpose |
| --- | --- |
| `config/lhs/<region>/` | LHS parameter bounds and sample-count CSVs |
| `config/scenario.example.json` | Template for adding a custom scenario |
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

1. Review/edit its bounds and run settings under `config/lhs/<region>/`.
   The bounds CSV columns are `index,base,min,max,name`. Parameter indices
   must start at 0 and be contiguous; the first three positions are populated
   with weather temperature, humidity, and pressure by the simulation. Set
   both `min` and `max` to vary a parameter, or leave both empty to use `base`.
2. Generate samples:

   ```text
   python -m green_metrics sample --scenario sri_lanka_dx
   ```

3. Put EPW files in `data/epw_files/<region>/` and ensure the required COP
   model pickle files are available.
4. Run all EPW files for the scenario:

   ```text
   python -m green_metrics simulate --scenario sri_lanka_dx
   ```

5. Find the Excel workbooks under `output/<region>/`. Each workbook has one
   sheet per generated parameter sample. Existing workbooks are skipped; remove
   or move an old workbook to rerun that location.

Built-in scenario names are `sri_lanka_dx`, `sri_lanka_air_chiller`,
`sri_lanka_chiller`, `sri_lanka_we_chiller_colo`,
`sri_lanka_ae_chiller_colo`, `usa_dx`, `usa_air_chiller`, `usa_chiller`,
`usa_we_chiller_colo`, and `usa_ae_chiller_colo`.

## Add your own data/scenario

The scenario JSON makes the locations and model selection configurable. Copy
`config/scenario.example.json` to a new JSON file and replace the example
values. Its paths can be absolute or relative to the data root supplied with
`--root` (by default, the installed project root).

1. Create a bounds CSV and a run CSV. Use an included pair as a template. The
   run CSV must contain `key,value` rows including `n_samples`; `random_seed`
   is optional.
2. Put your EPW input file(s) in the configured `weather_dir`.
3. Set `bounds_file`, `run_file`, `samples_file`, `weather_dir`, and
   `output_dir` in the scenario JSON. Set `model_dir` if your compatible COP
   pickles are not in `<root>/data/pkl_files`.
4. Choose a built-in `sim_func` implemented by this package:
   `PUE_WUE_DX`, `PUE_WUE_AIRChiller`, `PUE_WUE_Chiller`,
   `PUE_WUE_WE_Chiller_Colo`, or `PUE_WUE_AE_Chiller_Colo`. Make `sheet_prefix`,
   `pue_column`, and `wue_column` labels appropriate for your model.
5. Generate the parameter matrix and run simulations:

   ```text
   python -m green_metrics sample --config config/my_scenario.json --root .
   python -m green_metrics simulate --config config/my_scenario.json --root .
   ```

   The sample CSV is written to `samples_file`; result workbooks are written to
   `output_dir`. Use the same scenario file and data root for both commands.

The sample matrix columns are consumed positionally by the selected simulation
function, so the bounds CSV indices and base values must match that function's
expected parameter order. To add a new cooling-system model, implement its
function in `green_metrics.simulation.dc` and use that function name as
`sim_func`.

After installation, the equivalent console command is `green-metrics`; for
example, `green-metrics sample --scenario usa_chiller`.

## Attribution

This project builds on
[Data-Center-Water-footprint](https://github.com/nuoaleon/Data-Center-Water-footprint);
credit to @nuoaleon.
