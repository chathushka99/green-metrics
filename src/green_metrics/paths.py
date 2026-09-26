"""Resolved paths relative to the repository root."""

from pathlib import Path


def project_root() -> Path:
    """Directory containing ``pyproject.toml`` (repository root).

    Walks upward from this file so ``pip install -e .`` and running from a
    clone both resolve data paths correctly.
    """
    here = Path(__file__).resolve()
    for d in [here.parent] + list(here.parents):
        if (d / "pyproject.toml").is_file():
            return d
    raise RuntimeError(
        "Could not find project root (pyproject.toml). Install with pip install -e . from the repo."
    )
