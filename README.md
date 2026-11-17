# Member 2: Search & Path Planning

Path planning (BFS, Dijkstra, Greedy, A\*) and adaptive navigation (replanning, plus wait-or-detour around moving guards).

## Files

| File | Purpose |
|---|---|
| `search.py` | `plan()`, `path_still_valid()`, `navigate()`, heuristics |
| `demo_search.py` | Terminal demo: algorithm table, explored-area pictures, live escape |
| `benchmark_search.py` | 960-run experiment → CSV + charts in `results/` |
| `results/` | Benchmark output, already generated (CSV + 3 PNG charts) |
| `tests/test_search.py` | 69 pytest tests |
| `REPORT_SECTION.md` | Draft of the "Search & Replanning" report section, with real results |

## Run

This folder expects `member_1` next to it, which is the layout you received. In the merged repo, put the files in the same folder and it works the same way.

```bash
python demo_search.py                         # compare 4 algorithms on all levels
python demo_search.py --watch 3               # watch A* escape level 3 live
python demo_search.py --watch 3 --algo bfs --strategy replan
python benchmark_search.py                    # full experiment (~5 s)
pytest tests
```

Requires Python 3.10+ and pytest. matplotlib is optional and only needed for the charts.

## API for other members (do not rename)

```python
from search import plan, path_still_valid, navigate, ALGORITHMS

path, stats = plan(env, start, goal, algo="astar")
# algo in ("bfs", "dijkstra", "greedy", "astar")
# path = [(r,c), ...] start..goal inclusive, or None
# stats = {"algo", "found", "nodes_expanded", "path_cost", "path_length", "time_ms"}

path, stats, explored = plan(env, s, g, return_explored=True)   # for the GUI overlay
plan(env, s, g, avoid_obstacles=True)    # +5 cost next to guards
plan(env, s, g, ignore_obstacles=True)   # plan as if guards weren't there

path_still_valid(env, path, from_index)  # False -> Member 4's FSM enters REPLAN

log = navigate(env, start, goal, algo="astar", start_step=step,
               obstacle_strategy="wait_or_detour")   # or "replan"
# log: success, steps, end_step, end_pos, path_taken, path_cost,
#      replans, waits, plans, nodes_expanded, planning_time_ms, events
```

`navigate()` is the reference movement loop. Member 4's FSM can call it once per leg (S→K, K→T, T→E), or copy its per-step logic into the movement states. Pass `on_step=callback` to redraw the GUI after every step.

`search.py` does **not** import `environment.py`. It only needs an object with `neighbors`, `cost` and `is_blocked`, so Member 4's stubs work with it too.

## Design decisions

- **One best-first function covers 3 algorithms.** A\*, Dijkstra and Greedy differ only in the priority they sort by, which keeps the comparison fair.
- **Node counting:** `nodes_expanded` counts nodes popped from the frontier and expanded, not nodes pushed. Stale heap entries are skipped through the closed set.
- **Heuristic:** Manhattan distance. It's admissible and consistent here (4-directional movement, minimum step cost 1), so A\* is optimal. A test checks admissibility on every cell.
- **Tie-breaking:** ties are broken by insertion order (a counter), so runs are deterministic.
- **Two kinds of change are handled differently:**
  - **Permanent (collapse, door):** the whole remaining path is checked every step, and the agent replans from its current position if any cell is now a wall.
  - **Temporary (guards):** handled only when a guard is in the next cell. `wait_or_detour` takes the detour if it costs ≤ 6 extra, otherwise waits, but for at most 4 steps in a row to avoid deadlock. `replan` treats the guard as a wall (the baseline).

