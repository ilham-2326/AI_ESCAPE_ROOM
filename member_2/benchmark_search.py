"""
benchmark_search.py - Member 2 experiments (hand results/ to Member 5)

Runs a full escape (S->K->T->E, door opened after T) for
  levels 1-3 x 4 algorithms x 2 obstacle strategies x 30 seeds
  + 30 random generated levels x 4 algorithms x 2 strategies
and writes
  results/search_benchmark.csv    one row per run
  results/search_summary.csv      mean / std per configuration
  results/*.png                   charts (if matplotlib is installed)

  python benchmark_search.py            # full run (~10 s)
  python benchmark_search.py --seeds 5  # quick run
"""
import argparse
import csv
import os
import statistics as stats
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(os.path.dirname(HERE), "member_1")]
from environment import load_level              # noqa: E402
from level_generator import random_level        # noqa: E402
from search import ALGORITHMS, navigate, plan   # noqa: E402

STRATEGIES = ("replan", "wait_or_detour")
METRICS = ("success", "steps", "path_cost", "nodes_expanded", "replans",
           "waits", "planning_time_ms")


def escape(env, algo, strategy, max_steps=500):
    step, pos = 0, env.start
    out = {"success": 1, "steps": 0, "path_cost": 0, "nodes_expanded": 0,
           "replans": 0, "waits": 0, "planning_time_ms": 0.0}
    for i, goal in enumerate((env.key_pos, env.terminal_pos, env.exit)):
        if i == 2:
            env.door_open = True
        log = navigate(env, pos, goal, algo, start_step=step,
                       obstacle_strategy=strategy, max_steps=max_steps)
        for k in ("path_cost", "nodes_expanded", "replans", "waits", "planning_time_ms"):
            out[k] += log[k]
        step, pos = log["end_step"], log["end_pos"]
        if not log["success"]:
            out["success"] = 0
            break
    out["steps"] = step
    return out


def static_optimum(env):
    """Best possible cost if nothing moved (lower bound for comparison)."""
    e = env
    e.door_open = True
    total = 0
    for a, b in ((e.start, e.key_pos), (e.key_pos, e.terminal_pos), (e.terminal_pos, e.exit)):
        _, st = plan(e, a, b, "dijkstra", ignore_obstacles=True)
        total += st["path_cost"]
    e.reset()
    return total


def main(n_seeds):
    os.makedirs(os.path.join(HERE, "results"), exist_ok=True)
    rows = []
    t0 = time.time()
    worlds = [(f"L{lv}", lambda s, lv=lv: load_level(lv, seed=s)) for lv in (1, 2, 3)]
    worlds.append(("random", lambda s: random_level(s)))
    for name, make in worlds:
        for seed in range(1, n_seeds + 1):
            opt = static_optimum(make(seed))
            for algo in ALGORITHMS:
                for strat in STRATEGIES:
                    r = escape(make(seed), algo, strat)
                    r.update({"world": name, "seed": seed, "algo": algo,
                              "strategy": strat, "static_optimum": opt,
                              "cost_ratio": r["path_cost"] / opt})
                    rows.append(r)

    cols = ["world", "seed", "algo", "strategy", *METRICS, "static_optimum", "cost_ratio"]
    with open(os.path.join(HERE, "results", "search_benchmark.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    summary = []
    for name, _ in worlds:
        for algo in ALGORITHMS:
            for strat in STRATEGIES:
                sel = [r for r in rows if r["world"] == name and r["algo"] == algo
                       and r["strategy"] == strat]
                row = {"world": name, "algo": algo, "strategy": strat, "n": len(sel)}
                for m in METRICS + ("cost_ratio",):
                    vals = [r[m] for r in sel]
                    row[m + "_mean"] = round(stats.mean(vals), 3)
                    row[m + "_std"] = round(stats.pstdev(vals), 3)
                summary.append(row)
    with open(os.path.join(HERE, "results", "search_summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)

    print(f"{len(rows)} runs in {time.time() - t0:.1f}s\n")
    print(f"{'world':<7}{'algo':<9}{'strategy':<16}{'success':>8}{'steps':>9}"
          f"{'cost':>9}{'cost/opt':>9}{'expanded':>10}{'replans':>8}{'waits':>7}")
    for s in summary:
        print(f"{s['world']:<7}{s['algo']:<9}{s['strategy']:<16}"
              f"{s['success_mean'] * 100:>7.0f}%{s['steps_mean']:>9.1f}"
              f"{s['path_cost_mean']:>9.1f}{s['cost_ratio_mean']:>9.2f}"
              f"{s['nodes_expanded_mean']:>10.0f}{s['replans_mean']:>8.1f}{s['waits_mean']:>7.1f}")
    charts(summary, [w for w, _ in worlds])


def charts(summary, worlds):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - skipping charts)")
        return
    out = os.path.join(HERE, "results")
    colors = {"bfs": "#7f8c8d", "dijkstra": "#2e86de", "greedy": "#e67e22", "astar": "#27ae60"}

    def grouped(metric, strat, title, fname, ylabel):
        fig, ax = plt.subplots(figsize=(8, 4.2))
        width = 0.2
        for i, algo in enumerate(ALGORITHMS):
            m = [next(s for s in summary if s["world"] == w and s["algo"] == algo
                      and s["strategy"] == strat)[metric + "_mean"] for w in worlds]
            sd = [next(s for s in summary if s["world"] == w and s["algo"] == algo
                       and s["strategy"] == strat)[metric + "_std"] for w in worlds]
            xs = [x + (i - 1.5) * width for x in range(len(worlds))]
            ax.bar(xs, m, width, yerr=sd, capsize=3, label=algo, color=colors[algo])
        ax.set_xticks(range(len(worlds)), worlds)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.legend(frameon=False)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(os.path.join(out, fname), dpi=150)
        plt.close(fig)

    grouped("nodes_expanded", "wait_or_detour", "Nodes expanded per escape (mean ± sd)",
            "nodes_expanded.png", "nodes expanded")
    grouped("cost_ratio", "wait_or_detour", "Path cost relative to static optimum (1.0 = optimal)",
            "cost_ratio.png", "cost / static optimum")

    # strategy comparison for A*
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    for ax, metric, label in ((axes[0], "steps", "steps to escape"),
                              (axes[1], "replans", "replans")):
        for j, strat in enumerate(STRATEGIES):
            m = [next(s for s in summary if s["world"] == w and s["algo"] == "astar"
                      and s["strategy"] == strat)[metric + "_mean"] for w in worlds]
            ax.bar([x + (j - 0.5) * 0.35 for x in range(len(worlds))], m, 0.35,
                   label=strat, color=("#c0392b", "#27ae60")[j])
        ax.set_xticks(range(len(worlds)), worlds)
        ax.set_title(f"A*: {label}")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(out, "strategy_comparison.png"), dpi=150)
    plt.close(fig)
    print("\ncharts saved to results/")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    main(ap.parse_args().seeds)
