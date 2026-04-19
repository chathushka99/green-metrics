"""Run EPW batch for scenario `usa_dx`."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from green_metrics.batch.run import run_scenario

if __name__ == "__main__":
    run_scenario("usa_dx")
