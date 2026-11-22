"""Scenario registry: LHS stems, sample filenames, simulation functions, Excel columns."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass(frozen=True)
class ScenarioConfig:
    region: str
    bounds_stem: str
    samples_csv: str
    sim_func: str
    sheet_prefix: str
    pue_column: str
    wue_column: str
    bounds_file: Optional[str] = None
    run_file: Optional[str] = None
    samples_file: Optional[str] = None
    weather_dir: Optional[str] = None
    output_dir: Optional[str] = None
    model_dir: Optional[str] = None

    @classmethod
    def from_json(cls, path: Path) -> "ScenarioConfig":
        """Load a user-defined scenario with paths relative to the data root."""
        with path.open("r", encoding="utf-8") as config_file:
            values = json.load(config_file)

        if not isinstance(values, dict):
            raise ValueError(f"Scenario configuration must be a JSON object: {path}")

        required = {
            "region",
            "sim_func",
            "sheet_prefix",
            "pue_column",
            "wue_column",
            "bounds_file",
            "run_file",
            "samples_file",
            "weather_dir",
            "output_dir",
        }
        missing = sorted(required.difference(values))
        if missing:
            raise ValueError(
                f"Scenario configuration is missing {', '.join(missing)}: {path}"
            )

        for key in required:
            if not isinstance(values[key], str) or not values[key].strip():
                raise ValueError(
                    f"Scenario configuration value for {key!r} must be a non-empty string: {path}"
                )

        values.setdefault("bounds_stem", "")
        values.setdefault("samples_csv", Path(values["samples_file"]).name)
        allowed = set(cls.__dataclass_fields__)
        unknown = sorted(set(values).difference(allowed))
        if unknown:
            raise ValueError(
                f"Unknown scenario configuration keys {', '.join(unknown)}: {path}"
            )
        string_fields = required.union({"bounds_stem", "samples_csv", "model_dir"})
        for key in string_fields.intersection(values):
            if (
                key not in required
                and values[key] is not None
                and not isinstance(values[key], str)
            ):
                raise ValueError(
                    f"Scenario configuration value for {key!r} must be a string: {path}"
                )
        return cls(**values)


def load_scenario(
    scenario_id: Optional[str] = None, config_file: Optional[Path] = None
) -> ScenarioConfig:
    if config_file is not None:
        return ScenarioConfig.from_json(Path(config_file))
    if scenario_id not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario_id}")
    return SCENARIOS[scenario_id]


def resolve_path(root: Path, path: str) -> Path:
    path = Path(path)
    return path if path.is_absolute() else root / path


# (bounds stem, sim function, sheet prefix, result column suffix, sample-file stem)
_MODELS = {
    "dx": ("PUE_WUE_DX", "DX", "DX"),
    "air_chiller": ("PUE_WUE_AIRChiller", "AIRChiller", "AIRChiller"),
    "chiller": ("PUE_WUE_Chiller", "Chiller", "Chiller"),
    "we_chiller_colo": ("PUE_WUE_WE_Chiller_Colo", "WE_Chiller", "WE_Chiller"),
    "ae_chiller_colo": ("PUE_WUE_AE_Chiller_Colo", "AE_Chiller", "AE_Chiller"),
}
# region -> prefix of the sample file name (kept for the shipped data files)
_REGIONS = {"sri_lanka": "", "usa": "usa_"}


def _build_builtin() -> Dict[str, ScenarioConfig]:
    out: Dict[str, ScenarioConfig] = {}
    for region, file_prefix in _REGIONS.items():
        for stem, (func, sheet, column) in _MODELS.items():
            out[f"{region}_{stem}"] = ScenarioConfig(
                region=region,
                bounds_stem=stem,
                samples_csv=f"{file_prefix}{stem}_samples.csv",
                sim_func=func,
                sheet_prefix=sheet,
                pue_column=f"PUE_{column}",
                wue_column=f"WUE_{column}",
            )
    return out


SCENARIOS: Dict[str, ScenarioConfig] = _build_builtin()
