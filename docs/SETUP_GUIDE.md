# Setup guide – Python, virtual environment, first run

Tested on Windows 11 with **Python 3.12**. Supported: Python 3.10 – 3.13.
(Python 3.14+ is not recommended yet because scientific wheels such as CoolProp may be missing.)

## Fast path (recommended): `uv`

[`uv`](https://docs.astral.sh/uv/) downloads Python itself and keeps it private to this
project, so nothing else on your computer changes.

```powershell
# 1. install uv (once)
winget install --id=astral-sh.uv -e          # or: pip install uv

# 2. from the project folder
cd C:\Users\<you>\PycharmProjects\green-metrics
uv python install 3.12                       # downloads Python 3.12 (isolated)
uv venv --python 3.12 .venv                  # creates the virtual environment
uv pip install -r requirements.txt -e .      # installs libraries + this project
```

macOS/Linux: install uv with `curl -LsSf https://astral.sh/uv/install.sh | sh`, then the same commands
(activate with `source .venv/bin/activate`).

## Classic path: python.org + `venv`

1. **Install Python 3.12** – download the 64-bit installer from <https://www.python.org/downloads/>.
   Tick **"Add python.exe to PATH"** and install the **py launcher**.
   Check: `py -3.12 --version` → `Python 3.12.x`.
2. **Open PowerShell in the project folder** (`green-metrics`).
3. **Create the virtual environment**
   ```powershell
   py -3.12 -m venv .venv
   ```
4. **Activate it** (the prompt shows `(.venv)`)
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks scripts: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, or use `.\.venv\Scripts\activate.bat` in cmd.
   macOS/Linux: `python3.12 -m venv .venv && source .venv/bin/activate`.
5. **Install dependencies**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt -e .
   ```
6. **Verify**
   ```powershell
   python --version                     # 3.12.x
   python -m green_metrics list         # prints built-in scenarios
   python tests/check_models.py tests/gp_reference.json   # model files load correctly -> OK
   ```
7. **(Optional) Jupyter notebook**
   ```powershell
   python -m pip install -r requirements-notebook.txt
   python -m ipykernel install --user --name green-metrics --display-name "green-metrics (.venv)"
   python -m jupyter lab notebooks/green_metrics.ipynb
   ```
   Pick the kernel **green-metrics (.venv)**. In PyCharm/VS Code just select `.venv` as the interpreter.

Everything above is also automated: `.\run_green_metrics.bat -SetupOnly`.

## First run (command line)

```powershell
python -m green_metrics sample   --scenario usa_dx     # 1. generate LHS parameter samples
python -m green_metrics simulate --scenario usa_dx     # 2. one Excel workbook per weather file in output/usa/
```

All-in-one: `.\run_green_metrics.bat -Scenario usa_dx`.
A full year (8,760 h) × 50 samples is slow (CoolProp is called per hour); lower `n_samples` in
`config/lhs/<region>/*_run.csv` for a quick check.

## Use your own data

```powershell
python -m green_metrics init kenya --template usa_chiller   # creates config + data folders
```

Then:

1. Copy your weather files into `data/epw_files/kenya/` – `.epw`, **or** `.csv` with columns
   `T_oa` (°C), `RH_oa` (%), `P_oa` (Pa), one row per hour.
2. Edit `config/lhs/kenya/chiller_bounds.csv` (`index,base,min,max,name`): set `min`+`max` to sample
   a parameter, leave both empty to hold it at `base`. Rows 0-2 are the weather inputs; keep the order.
3. Set `n_samples` (and optional `random_seed`) in `chiller_run.csv`.
4. Run:
   ```powershell
   python -m green_metrics sample   --config config/scenarios/kenya.json
   python -m green_metrics simulate --config config/scenarios/kenya.json
   ```
   Add `--overwrite` to recompute existing workbooks.
5. Using your own COP models? Point `model_dir` in the JSON to a folder with `COP_2.pkl`, `COP_DX.pkl`, `COP_AC.pkl`
   (scikit-learn `GaussianProcessRegressor` pickles; only load files you trust).

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `py -3.12` not found | Install Python 3.12 (or use `uv`). |
| `No matching distribution for CoolProp` | You are on Python 3.14+ or 32-bit Python; use 3.12 64-bit. |
| Wrong Python inside `.venv` | Delete `.venv` and recreate it (step 3). |
| `ModuleNotFoundError: green_metrics` | Run `pip install -e .` inside the activated venv. |
| Notebook can't import packages | Select the `green-metrics (.venv)` kernel. |
