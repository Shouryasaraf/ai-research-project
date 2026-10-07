"""Command-line runner for paired policy experiments and reproducible summaries."""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .analysis import write_summary
from .experiment_records import (
    ExperimentRecord,
    RunStatus,
    configuration_digest,
    write_immutable_record,
)
from .policies import PolicyVariant, run_policy
from .scenarios import ScenarioDefinition, load_scenario


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _environment() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "runner": "vfw_research.experiment_runner/1",
    }


def _selected_candidate(run, node_id: str | None):
    return next((candidate for candidate in run.candidates if candidate.node_id == node_id), None)


def run_experiment(
    scenario: ScenarioDefinition,
    *,
    output_root: Path,
    batch_id: str,
) -> Path:
    if not batch_id.strip() or any(character in batch_id for character in "/\\"):
        raise ValueError("batch_id must be a non-empty filename-safe identifier")
    raw_directory = output_root / "raw" / batch_id
    raw_directory.mkdir(parents=True, exist_ok=False)
    digest = configuration_digest(scenario.payload)
    environment = _environment()
    manifest = {
        "batch_id": batch_id,
        "scenario_id": scenario.scenario_id,
        "config_sha256": digest,
        "synthetic_inputs": scenario.synthetic_inputs,
        "seeds": list(scenario.seeds),
        "policies": [variant.value for variant in PolicyVariant],
        "evidence_class": "synthetic controller experiment; not a network benchmark",
        "environment": environment,
    }
    with (raw_directory / "manifest.json").open("x", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
        handle.write("\n")

    for seed in scenario.seeds:
        run = scenario.build_run(seed)
        for variant in PolicyVariant:
            started = _utc_now()
            start_clock = time.perf_counter()
            outcome = run_policy(variant, run)
            elapsed = time.perf_counter() - start_clock
            finished = _utc_now()
            selected = _selected_candidate(run, outcome.decision.selected_node_id)
            committed = outcome.decision.action.value == "COMMIT"
            record = ExperimentRecord(
                run_id=f"{batch_id}-s{seed}-{variant.value}",
                scenario_id=scenario.scenario_id,
                policy_id=variant.value,
                seed=seed,
                synthetic_inputs=scenario.synthetic_inputs,
                status=RunStatus.COMPLETED,
                started_utc=started,
                finished_utc=finished,
                config_sha256=digest,
                environment=environment,
                measured_metrics={"decision_duration_seconds": elapsed},
                modeled_metrics={
                    "net_benefit_utility": outcome.decision.net_benefit,
                    "adaptive_threshold_utility": outcome.decision.adaptive_threshold,
                    "migration_committed_count": 1.0 if committed else 0.0,
                    "selected_carbon_gco2_per_kwh": (
                        selected.carbon_gco2_per_kwh if selected else 0.0
                    ),
                    "selected_security_risk_score": selected.security_risk if selected else 0.0,
                },
                notes=(
                    "Controller-only synthetic experiment; no packet-path performance was measured.",
                    "Carbon intensity and security risk are modeled scenario inputs.",
                ),
                decision={
                    **outcome.decision.as_record(),
                    "migration_mode": outcome.migration_mode,
                },
            )
            write_immutable_record(raw_directory, record)
    return raw_directory


def _default_batch_id() -> str:
    return datetime.now(timezone.utc).strftime("pilot-%Y%m%dT%H%M%SZ")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    plan = subparsers.add_parser("plan", help="validate and print the experiment plan")
    plan.add_argument("scenario", type=Path)
    run = subparsers.add_parser("run", help="run all policies for every declared seed")
    run.add_argument("scenario", type=Path)
    run.add_argument("--output-root", type=Path, default=Path("artifacts"))
    run.add_argument("--batch-id", default=None)
    summarize = subparsers.add_parser("summarize", help="rebuild artifacts from raw records")
    summarize.add_argument("raw_directory", type=Path)
    summarize.add_argument("output_directory", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "plan":
        scenario = load_scenario(args.scenario)
        print(
            json.dumps(
                {
                    "scenario_id": scenario.scenario_id,
                    "synthetic_inputs": scenario.synthetic_inputs,
                    "seeds": list(scenario.seeds),
                    "policies": [variant.value for variant in PolicyVariant],
                    "planned_records": len(scenario.seeds) * len(PolicyVariant),
                },
                indent=2,
            )
        )
        return 0
    if args.command == "run":
        scenario = load_scenario(args.scenario)
        batch_id = args.batch_id or _default_batch_id()
        raw_directory = run_experiment(
            scenario, output_root=args.output_root, batch_id=batch_id
        )
        processed = args.output_root / "processed" / batch_id
        outputs = write_summary(raw_directory, processed)
        print(json.dumps({"raw": str(raw_directory), "outputs": [str(p) for p in outputs]}, indent=2))
        return 0
    outputs = write_summary(args.raw_directory, args.output_directory)
    print(json.dumps({"outputs": [str(path) for path in outputs]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
