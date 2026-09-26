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


SCENARIOS: Dict[str, ScenarioConfig] = {
    "sri_lanka_dx": ScenarioConfig(
        region="sri_lanka",
        bounds_stem="dx",
        samples_csv="dx_samples.csv",
        sim_func="PUE_WUE_DX",
        sheet_prefix="DX",
        pue_column="PUE_DX",
        wue_column="WUE_DX",
    ),
    "sri_lanka_air_chiller": ScenarioConfig(
        region="sri_lanka",
        bounds_stem="air_chiller",
        samples_csv="air_chiller_samples.csv",
        sim_func="PUE_WUE_AIRChiller",
        sheet_prefix="AIRChiller",
        pue_column="PUE_AIRChiller",
        wue_column="WUE_AIRChiller",
    ),
    "sri_lanka_chiller": ScenarioConfig(
        region="sri_lanka",
        bounds_stem="chiller",
        samples_csv="chiller_samples.csv",
        sim_func="PUE_WUE_Chiller",
        sheet_prefix="Chiller",
        pue_column="PUE_Chiller",
        wue_column="WUE_Chiller",
    ),
    "sri_lanka_we_chiller_colo": ScenarioConfig(
        region="sri_lanka",
        bounds_stem="we_chiller_colo",
        samples_csv="we_chiller_colo_samples.csv",
        sim_func="PUE_WUE_WE_Chiller_Colo",
        sheet_prefix="WE_Chiller",
        pue_column="PUE_WE_Chiller",
        wue_column="WUE_WE_Chiller",
    ),
    "sri_lanka_ae_chiller_colo": ScenarioConfig(
        region="sri_lanka",
        bounds_stem="ae_chiller_colo",
        samples_csv="ae_chiller_colo_samples.csv",
        sim_func="PUE_WUE_AE_Chiller_Colo",
        sheet_prefix="AE_Chiller",
        pue_column="PUE_AE_Chiller",
        wue_column="WUE_AE_Chiller",
    ),
    "usa_dx": ScenarioConfig(
        region="usa",
        bounds_stem="dx",
        samples_csv="usa_dx_samples.csv",
        sim_func="PUE_WUE_DX",
        sheet_prefix="DX",
        pue_column="PUE_DX",
        wue_column="WUE_DX",
    ),
    "usa_air_chiller": ScenarioConfig(
        region="usa",
        bounds_stem="air_chiller",
        samples_csv="usa_air_chiller_samples.csv",
        sim_func="PUE_WUE_AIRChiller",
        sheet_prefix="AIRChiller",
        pue_column="PUE_AIRChiller",
        wue_column="WUE_AIRChiller",
    ),
    "usa_chiller": ScenarioConfig(
        region="usa",
        bounds_stem="chiller",
        samples_csv="usa_chiller_samples.csv",
        sim_func="PUE_WUE_Chiller",
        sheet_prefix="Chiller",
        pue_column="PUE_Chiller",
        wue_column="WUE_Chiller",
    ),
    "usa_we_chiller_colo": ScenarioConfig(
        region="usa",
        bounds_stem="we_chiller_colo",
        samples_csv="usa_we_chiller_colo_samples.csv",
        sim_func="PUE_WUE_WE_Chiller_Colo",
        sheet_prefix="WE_Chiller",
        pue_column="PUE_WE_Chiller",
        wue_column="WUE_WE_Chiller",
    ),
    "usa_ae_chiller_colo": ScenarioConfig(
        region="usa",
        bounds_stem="ae_chiller_colo",
        samples_csv="usa_ae_chiller_colo_samples.csv",
        sim_func="PUE_WUE_AE_Chiller_Colo",
        sheet_prefix="AE_Chiller",
        pue_column="PUE_AE_Chiller",
        wue_column="WUE_AE_Chiller",
    ),
}
