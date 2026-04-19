"""Regenerate LHS CSV for scenario `usa_chiller`. Prefer: python -m green_metrics sample --scenario usa_chiller"""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from green_metrics.sampling.generate import write_samples_for_scenario

if __name__ == "__main__":
    print(write_samples_for_scenario("usa_chiller"))
