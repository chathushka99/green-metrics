"""Backward-compatible import path; implementation lives in ``green_metrics.simulation.dc``."""

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from green_metrics.simulation.dc import *  # noqa: F403
