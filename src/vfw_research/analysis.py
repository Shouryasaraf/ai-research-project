"""Rebuild deterministic summary artifacts from immutable experiment records."""

from __future__ import annotations

import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def _bootstrap_mean_ci(values: list[float], *, seed: int = 20261006) -> tuple[float, float]:
    if not values:
        raise ValueError("cannot summarize an empty metric")
    if len(values) == 1:
        return values[0], values[0]
    generator = random.Random(seed)
    means = sorted(
        statistics.fmean(generator.choice(values) for _ in values) for _ in range(2000)
    )
    return means[int(0.025 * len(means))], means[int(0.975 * len(means)) - 1]


def read_records(directory: Path) -> list[dict]:
    records: list[dict] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.json")):
        if path.name == "manifest.json":
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        run_id = str(record.get("run_id", ""))
        if not run_id or run_id in seen:
            raise ValueError(f"missing or duplicate run_id in {path}")
        seen.add(run_id)
        if record.get("status") != "completed":
            continue
        records.append(record)
    if not records:
        raise ValueError(f"no completed experiment records found in {directory}")
    return records


def build_summary(records: Iterable[dict]) -> dict:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        grouped[str(record["policy_id"])].append(record)
    policies: list[dict] = []
    for policy_id in sorted(grouped):
        rows = grouped[policy_id]
        actions = Counter(str(row["decision"]["action"]) for row in rows)
        net_benefits = [float(row["modeled_metrics"]["net_benefit_utility"]) for row in rows]
        decision_times = [
            float(row["measured_metrics"]["decision_duration_seconds"]) for row in rows
        ]
        low, high = _bootstrap_mean_ci(net_benefits)
        policies.append(
            {
                "policy_id": policy_id,
                "completed_runs": len(rows),
                "action_counts": dict(sorted(actions.items())),
                "commit_rate": actions["COMMIT"] / len(rows),
                "net_benefit_utility_mean": statistics.fmean(net_benefits),
                "net_benefit_utility_bootstrap_ci95": [low, high],
                "decision_duration_seconds_mean": statistics.fmean(decision_times),
            }
        )
    return {
        "evidence_class": "synthetic controller experiment; not a network benchmark",
        "completed_records": sum(item["completed_runs"] for item in policies),
        "policies": policies,
    }


def _write_svg(path: Path, policies: list[dict]) -> None:
    width = 960
    row_height = 34
    height = 70 + row_height * len(policies)
    label_width = 320
    chart_width = 560
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,sans-serif;fill:#172033}.title{font-size:18px;font-weight:700}.label{font-size:12px}.value{font-size:12px;font-weight:700}</style>',
        '<text x="20" y="28" class="title">Synthetic controller commit rate by policy</text>',
        '<text x="20" y="48" class="label">Generated from immutable records; not a network-performance result</text>',
    ]
    for index, item in enumerate(policies):
        y = 66 + index * row_height
        rate = float(item["commit_rate"])
        bar_width = chart_width * rate
        label = str(item["policy_id"])
        lines.extend(
            [
                f'<text x="20" y="{y + 16}" class="label">{label}</text>',
                f'<rect x="{label_width}" y="{y}" width="{chart_width}" height="20" rx="3" fill="#e7edf5"/>',
                f'<rect x="{label_width}" y="{y}" width="{bar_width:.2f}" height="20" rx="3" fill="#2563eb"/>',
                f'<text x="{label_width + chart_width + 10}" y="{y + 15}" class="value">{rate:.0%}</text>',
            ]
        )
    lines.append("</svg>")
    with path.open("x", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


def write_summary(raw_directory: Path, output_directory: Path) -> tuple[Path, Path, Path]:
    records = read_records(raw_directory)
    summary = build_summary(records)
    output_directory.mkdir(parents=True, exist_ok=False)
    json_path = output_directory / "summary.json"
    with json_path.open("x", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, sort_keys=True)
        handle.write("\n")
    csv_path = output_directory / "policy_summary.csv"
    with csv_path.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "policy_id",
                "completed_runs",
                "commit_rate",
                "net_benefit_utility_mean",
                "net_benefit_ci95_low",
                "net_benefit_ci95_high",
                "decision_duration_seconds_mean",
            ]
        )
        for item in summary["policies"]:
            low, high = item["net_benefit_utility_bootstrap_ci95"]
            writer.writerow(
                [
                    item["policy_id"],
                    item["completed_runs"],
                    item["commit_rate"],
                    item["net_benefit_utility_mean"],
                    low,
                    high,
                    item["decision_duration_seconds_mean"],
                ]
            )
    svg_path = output_directory / "commit_rate.svg"
    _write_svg(svg_path, summary["policies"])
    return json_path, csv_path, svg_path
