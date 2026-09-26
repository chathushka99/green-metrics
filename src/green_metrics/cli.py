"""Command-line interface."""

from __future__ import annotations

import argparse
from pathlib import Path

from green_metrics.batch.registry import SCENARIOS
from green_metrics.batch.run import run_scenario
from green_metrics.sampling.generate import write_samples_for_scenario


def main() -> None:
    parser = argparse.ArgumentParser(prog="green-metrics")
    sub = parser.add_subparsers(dest="command", required=True)

    p_sample = sub.add_parser("sample", help="Generate LHS sample CSV from config/lhs")
    sample_source = p_sample.add_mutually_exclusive_group(required=True)
    sample_source.add_argument(
        "--scenario", choices=sorted(SCENARIOS.keys()), help="Built-in scenario id"
    )
    sample_source.add_argument(
        "--config", type=Path, help="Path to a custom scenario JSON file"
    )
    p_sample.add_argument(
        "--root", type=Path, help="Data/project root (defaults to this installation)"
    )

    p_sim = sub.add_parser("simulate", help="Run EPW batch simulation for one scenario")
    sim_source = p_sim.add_mutually_exclusive_group(required=True)
    sim_source.add_argument(
        "--scenario", choices=sorted(SCENARIOS.keys()), help="Built-in scenario id"
    )
    sim_source.add_argument(
        "--config", type=Path, help="Path to a custom scenario JSON file"
    )
    p_sim.add_argument(
        "--root", type=Path, help="Data/project root (defaults to this installation)"
    )

    args = parser.parse_args()
    if args.command == "sample":
        path = write_samples_for_scenario(args.scenario, args.config, args.root)
        print(f"Wrote: {path}")
    elif args.command == "simulate":
        run_scenario(args.scenario, args.config, args.root)


if __name__ == "__main__":
    main()
