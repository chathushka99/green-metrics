#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

usage() {
    cat <<'EOF'
Usage:
  ./run_green_metrics.sh [--scenario SCENARIO | --config FILE] [--root DIR]

Examples:
  ./run_green_metrics.sh
  ./run_green_metrics.sh --scenario usa_chiller
  ./run_green_metrics.sh --config config/my_scenario.json
EOF
}

SCENARIO=""
CONFIG=""
DATA_ROOT="$ROOT"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --scenario)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            SCENARIO="$2"
            shift 2
            ;;
        --config)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            CONFIG="$2"
            shift 2
            ;;
        --root)
            [[ $# -ge 2 ]] || { usage >&2; exit 2; }
            DATA_ROOT="$2"
            shift 2
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ -n "$SCENARIO" && -n "$CONFIG" ]]; then
    echo "Specify either --scenario or --config, not both." >&2
    exit 2
fi

if ! command -v python3.7 >/dev/null 2>&1; then
    echo "CPython 3.7 was not found. Install CPython 3.7.9, then rerun this script." >&2
    echo "Download: https://www.python.org/downloads/release/python-379/" >&2
    exit 1
fi

PYTHON_VERSION="$(python3.7 --version 2>&1)"
if [[ ! "$PYTHON_VERSION" =~ ^Python\ 3\.7\. ]]; then
    echo "python3.7 resolved to '$PYTHON_VERSION'; CPython 3.7 is required." >&2
    exit 1
fi

VENV="$ROOT/.venv"
VENV_PYTHON="$VENV/bin/python"
if [[ ! -x "$VENV_PYTHON" ]]; then
    python3.7 -m venv "$VENV"
fi

VENV_VERSION="$("$VENV_PYTHON" --version 2>&1)"
if [[ ! "$VENV_VERSION" =~ ^Python\ 3\.7\. ]]; then
    echo "$VENV uses $VENV_VERSION; this project requires Python 3.7." >&2
    echo "Rename or remove .venv and rerun this script." >&2
    exit 1
fi

echo "Installing the pinned project dependencies..."
"$VENV_PYTHON" -m pip install --upgrade 'pip<24.1'
"$VENV_PYTHON" -m pip install -e .

CLI_ARGS=()
if [[ -n "$CONFIG" ]]; then
    if [[ "$CONFIG" != /* ]]; then
        CONFIG="$ROOT/$CONFIG"
    fi
    CLI_ARGS+=(--config "$CONFIG")
else
    SCENARIO="${SCENARIO:-sri_lanka_dx}"
    CLI_ARGS+=(--scenario "$SCENARIO")
fi
CLI_ARGS+=(--root "$DATA_ROOT")

echo "Generating LHS samples..."
"$VENV_PYTHON" -m green_metrics sample "${CLI_ARGS[@]}"

echo "Running EPW simulations..."
"$VENV_PYTHON" -m green_metrics simulate "${CLI_ARGS[@]}"

echo "Finished. Results are in the configured output directory."
