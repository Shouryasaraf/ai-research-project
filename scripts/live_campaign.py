"""Plan or execute matched family batches without shell interpolation."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from vfw_research.policies import PolicyVariant

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true", help="default is read-only plan")
    parser.add_argument("--families", nargs="+", choices=["step", "steady", "bursts", "trend", "flash"],
                        default=["steady", "bursts", "trend", "flash"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[31])
    parser.add_argument("--steps", type=int, default=12)
    parser.add_argument("--flows", type=int, default=3)
    parser.add_argument("--policies", nargs="+", choices=[policy.value for policy in PolicyVariant],
                        default=["full_proposed_controller", "reactive_threshold"])
    args = parser.parse_args()
    if (not 6 <= args.steps <= 120 or not 1 <= args.flows <= 16 or any(seed < 0 for seed in args.seeds)
        or any(len(values) != len(set(values)) for values in (args.seeds, args.policies, args.families))):
        parser.error("invalid bounds or duplicate campaign values")
    plan = {"phase": "exploratory", "families": args.families, "seeds": args.seeds,
            "policies": args.policies, "steps": args.steps, "flows": args.flows,
            "planned_trials": len(args.families)*len(args.seeds)*len(args.policies)}
    print(json.dumps(plan, indent=2), flush=True)
    if not args.execute:
        return
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "campaign.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    for family in args.families:
        subprocess.run([sys.executable, str(ROOT / "scripts/live_experiment_batch.py"),
                        "--output", str(args.output / family), "--family", family,
                        "--steps", str(args.steps), "--flows", str(args.flows),
                        "--seeds", *map(str, args.seeds), "--policies", *args.policies], check=True)

if __name__ == "__main__":
    main()
