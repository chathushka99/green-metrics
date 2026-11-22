"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from green_metrics.batch.registry import SCENARIOS
from green_metrics.batch.run import run_scenario
from green_metrics.sampling.generate import write_samples_for_scenario
from green_metrics.scaffold import init_scenario


def _add_scenario_args(p: argparse.ArgumentParser) -> None:
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--scenario", choices=sorted(SCENARIOS), help="Built-in scenario id"
    )
    source.add_argument("--config", type=Path, help="Path to a scenario JSON file")
    p.add_argument(
        "--root", type=Path, help="Data/project root (defaults to this installation)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(prog="green-metrics")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sample = sub.add_parser("sample", help="Generate the LHS sample CSV")
    _add_scenario_args(p_sample)

    p_sim = sub.add_parser("simulate", help="Run every weather file in a scenario")
    _add_scenario_args(p_sim)
    p_sim.add_argument(
        "--overwrite", action="store_true", help="Recompute existing output workbooks"
    )

    sub.add_parser("list", help="List built-in scenarios")

    p_init = sub.add_parser("init", help="Scaffold a new scenario for your own data")
    p_init.add_argument("name", help="Name of the new scenario/region, e.g. kenya")
    p_init.add_argument(
        "--template", default="usa_dx", choices=sorted(SCENARIOS),
        help="Built-in scenario whose bounds/run CSVs are copied (default: usa_dx)",
    )
    p_init.add_argument("--root", type=Path, help="Where to create the files (default: here)")

    args = parser.parse_args()
    if args.command == "sample":
        print(f"Wrote: {write_samples_for_scenario(args.scenario, args.config, args.root)}")
    elif args.command == "simulate":
        run_scenario(args.scenario, args.config, args.root, args.overwrite)
    elif args.command == "list":
        for name, cfg in sorted(SCENARIOS.items()):
            print(f"{name:28s} {cfg.sim_func}")
    elif args.command == "init":
        path = init_scenario(args.name, args.template, args.root or Path.cwd())
        print(f"Created {path}\nNext: put weather files in the weather_dir, edit the bounds CSV, then run\n"
              f"  green-metrics sample --config {path}\n  green-metrics simulate --config {path}")


if __name__ == "__main__":
    main()
