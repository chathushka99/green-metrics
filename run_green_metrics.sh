#!/usr/bin/env bash
# Create .venv (Python 3.12), install dependencies, then sample + simulate.
#   ./run_green_metrics.sh --scenario usa_chiller
#   ./run_green_metrics.sh --config config/scenarios/my_site.json [--root DIR] [--overwrite]
#   ./run_green_metrics.sh --setup-only
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
PYVER="${PYTHON_VERSION:-3.12}"
SCENARIO=""; CONFIG=""; DATA_ROOT="$PWD"; OVERWRITE=""; SETUP_ONLY=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --scenario) SCENARIO="$2"; shift 2;;
    --config) CONFIG="$2"; shift 2;;
    --root) DATA_ROOT="$2"; shift 2;;
    --overwrite) OVERWRITE="--overwrite"; shift;;
    --setup-only) SETUP_ONLY=1; shift;;
    -h|--help) sed -n 2,5p "$0"; exit 0;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done
[[ -n "$SCENARIO" && -n "$CONFIG" ]] && { echo "Use --scenario or --config, not both" >&2; exit 2; }

VENV_PY=".venv/bin/python"
if [[ ! -x "$VENV_PY" ]]; then
  if command -v uv >/dev/null; then uv venv --python "$PYVER" .venv
  elif command -v "python$PYVER" >/dev/null; then "python$PYVER" -m venv .venv
  else echo "Python $PYVER not found. See docs/SETUP_GUIDE.md (install uv or Python $PYVER)." >&2; exit 1; fi
fi
case "$($VENV_PY -c 'import sys;print("%d.%d"%sys.version_info[:2])')" in
  3.10|3.11|3.12|3.13) ;;
  *) echo ".venv uses an unsupported Python (need 3.10-3.13). Delete .venv and rerun." >&2; exit 1;;
esac

if command -v uv >/dev/null; then uv pip install --python "$VENV_PY" -r requirements.txt -e .
else "$VENV_PY" -m pip install --upgrade pip && "$VENV_PY" -m pip install -r requirements.txt -e .; fi
[[ -n "$SETUP_ONLY" ]] && { echo "Environment ready."; exit 0; }

if [[ -n "$CONFIG" ]]; then ARGS=(--config "$CONFIG"); else ARGS=(--scenario "${SCENARIO:-sri_lanka_dx}"); fi
ARGS+=(--root "$DATA_ROOT")
"$VENV_PY" -m green_metrics sample "${ARGS[@]}"
"$VENV_PY" -m green_metrics simulate "${ARGS[@]}" $OVERWRITE
echo "Finished. Results are in the scenario's output directory."
