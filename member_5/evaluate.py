#!/usr/bin/env python3
"""Member 5: reproducible, headless evaluation of the integrated AI agent.

Runs the integrated Member 4 FSM agent on the three hand-made levels with
all four Member 2 search algorithms. Each trial uses a fixed environment seed.
No Pygame window is opened.

Example:
    python member_5/evaluate.py
    python member_5/evaluate.py --seeds 1-30,44
    python member_5/evaluate.py --levels 1 2 3 --seeds 1-30 --max-steps 3000

Outputs:
    member_5/results/raw_results.csv
    member_5/results/run_metadata.json

CSV columns include completion time, path cost, states explored, success,
replans and waits. A trial that raises an exception is retained as a failed
row with its error message rather than silently discarded.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The project uses simple module imports (e.g. `from search import plan`).
# Put each member folder on sys.path before importing the integrated agent.
for folder in ("member_1", "member_2", "member_3", "member_4"):
    folder_path = str(ROOT / folder)
    if folder_path not in sys.path:
        sys.path.insert(0, folder_path)

from agent import Agent, State  # noqa: E402
from environment import load_level  # noqa: E402
from search import ALGORITHMS  # noqa: E402


DEFAULT_SEEDS = list(range(1, 31)) + [44]  # include the reported failure seed
DEFAULT_LEVELS = (1, 2, 3)
DEFAULT_ALGORITHMS = ALGORITHMS


def parse_seeds(value: str) -> list[int]:
    """Parse e.g. '1-30,44' into a sorted, unique list of integer seeds."""
    values: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start, end = int(start_text), int(end_text)
            if end < start:
                raise argparse.ArgumentTypeError(f"Invalid seed range: {part}")
            values.update(range(start, end + 1))
        else:
            values.add(int(part))
    if not values:
        raise argparse.ArgumentTypeError("At least one seed is required")
    if min(values) < 0:
        raise argparse.ArgumentTypeError("Seeds must be non-negative integers")
    return sorted(values)


def run_trial(level: int, algorithm: str, seed: int, max_steps: int) -> dict:
    """Run one independent trial and return one flat CSV-ready record."""
    # Ensure Python-side random choices are reproducible too.
    random.seed(seed)
    started = time.perf_counter()
    record = {
        "level": level,
        "algorithm": algorithm,
        "seed": seed,
        "success": False,
        "final_state": "NOT_STARTED",
        "completion_time_seconds": None,
        "simulation_steps": 0,
        "path_cost": 0,
        "states_explored": 0,
        "replans": 0,
        "waits": 0,
        "error": "",
    }
    agent = None
    try:
        env = load_level(level, seed=seed)
        agent = Agent(env, algorithm=algorithm)
        for _ in range(max_steps):
            if agent.state in (State.ESCAPED, State.FAILED):
                break
            agent.update()

        record["success"] = agent.state == State.ESCAPED
        record["final_state"] = agent.state.name
        record["simulation_steps"] = agent.step_count
        record["path_cost"] = agent.path_cost_total
        record["states_explored"] = agent.nodes_expanded
        record["replans"] = agent.replans
        record["waits"] = agent.waits
        if agent.state not in (State.ESCAPED, State.FAILED):
            record["final_state"] = "TIMEOUT"
    except Exception as exc:  # preserve failed trials for transparent analysis
        record["final_state"] = "ERROR"
        record["error"] = f"{type(exc).__name__}: {exc}"
        record["traceback"] = traceback.format_exc(limit=5)
        if agent is not None:
            record["simulation_steps"] = getattr(agent, "step_count", 0)
            record["path_cost"] = getattr(agent, "path_cost_total", 0)
            record["states_explored"] = getattr(agent, "nodes_expanded", 0)
            record["replans"] = getattr(agent, "replans", 0)
            record["waits"] = getattr(agent, "waits", 0)
    finally:
        record["completion_time_seconds"] = round(time.perf_counter() - started, 8)
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Headless AI Escape Room evaluation")
    parser.add_argument("--seeds", type=parse_seeds,
                        default=DEFAULT_SEEDS,
                        help="Fixed seeds, e.g. '1-30,44' (default: 1-30,44)")
    parser.add_argument("--levels", type=int, nargs="+", default=list(DEFAULT_LEVELS),
                        choices=(1, 2, 3), help="Hand-made levels to evaluate")
    parser.add_argument("--algorithms", nargs="+", default=list(DEFAULT_ALGORITHMS),
                        choices=DEFAULT_ALGORITHMS, help="Search algorithms")
    parser.add_argument("--max-steps", type=int, default=3000,
                        help="Maximum simulation ticks before a trial is marked TIMEOUT")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "member_5" / "results" / "raw_results.csv",
                        help="Output CSV path")
    args = parser.parse_args()

    if args.max_steps <= 0:
        parser.error("--max-steps must be positive")
    if len(args.seeds) < 30:
        parser.error("At least 30 fixed seeds are required by the project brief")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    combinations = [(level, algo, seed)
                    for level in args.levels
                    for algo in args.algorithms
                    for seed in args.seeds]
    print(f"Running {len(combinations)} trials: {len(args.levels)} levels x "
          f"{len(args.algorithms)} algorithms x {len(args.seeds)} seeds")
    print("No game window will be opened. Please wait...\n")

    rows = []
    for index, (level, algo, seed) in enumerate(combinations, start=1):
        row = run_trial(level, algo, seed, args.max_steps)
        rows.append(row)
        status = "SUCCESS" if row["success"] else row["final_state"]
        print(f"[{index:>3}/{len(combinations)}] L{level} {algo:<8} seed={seed:<3} "
              f"{status:<8} steps={row['simulation_steps']:<4} "
              f"expanded={row['states_explored']:<5} "
              f"replans={row['replans']:<3} waits={row['waits']:<3}")

    columns = [
        "level", "algorithm", "seed", "success", "final_state",
        "completion_time_seconds", "simulation_steps", "path_cost",
        "states_explored", "replans", "waits", "error",
    ]
    with args.output.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "script": "member_5/evaluate.py",
        "levels": args.levels,
        "algorithms": args.algorithms,
        "seeds": args.seeds,
        "seed_count": len(args.seeds),
        "max_steps": args.max_steps,
        "trial_count": len(rows),
        "success_count": sum(bool(row["success"]) for row in rows),
        "failure_count": sum(not bool(row["success"]) for row in rows),
        "output_csv": str(args.output.relative_to(ROOT)) if args.output.is_relative_to(ROOT) else str(args.output),
        "notes": [
            "completion_time_seconds is wall-clock runtime for one headless trial",
            "simulation_steps is the agent's tick count",
            "states_explored is the integrated agent's cumulative nodes_expanded counter",
            "path_cost is the agent's accumulated movement cost",
            "success is true only when the FSM reaches ESCAPED",
            "Seed 44 is included explicitly for failure-case inspection",
        ],
    }
    metadata_path = args.output.parent / "run_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print("\nEvaluation finished.")
    print(f"CSV: {args.output}")
    print(f"Metadata: {metadata_path}")
    print(f"Successful: {metadata['success_count']}/{metadata['trial_count']}")
    print(f"Failed/timeouts/errors: {metadata['failure_count']}/{metadata['trial_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
