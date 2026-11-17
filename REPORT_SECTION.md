# 5. Search & Replanning

## 5.1 Algorithms

The agent's navigation uses informed search, with three other algorithms implemented as baselines:

| Algorithm | Priority f(n) | Complete | Optimal (cost) | Notes |
|---|---|---|---|---|
| BFS | FIFO order | Yes | Only if all step costs are equal | Minimises the number of steps; ignores mud |
| Dijkstra (uniform-cost) | g(n) | Yes | Yes | Expands in every direction |
| Greedy best-first | h(n) | Yes (finite graph, closed set) | No | Very few expansions, but can take costly routes |
| **A\*** | g(n) + h(n) | Yes | **Yes** | Optimal, and expands far fewer nodes than Dijkstra |

Dijkstra, Greedy and A\* share one best-first implementation that differs only in the priority function, so their measured differences come from the algorithms rather than from the code. `nodes_expanded` counts nodes removed from the frontier and expanded (not nodes added to it). Duplicate heap entries are skipped using a closed set.

**Heuristic.** A\* uses the Manhattan distance h(n) = |r − r_g| + |c − c_g|. The agent moves in four directions and every step costs at least 1, so h never overestimates the true remaining cost, which makes it *admissible*. It is also *consistent*, because adjacent cells differ in h by exactly 1 ≤ step cost. A\* is therefore optimal, and never needs to re-expand a node once it is closed. An automated test confirms admissibility on every free cell of Level 3.

```
A*(start, goal):
    open ← priority queue {(h(start), start)};  g[start] ← 0;  closed ← ∅
    while open not empty:
        n ← pop lowest f
        if n ∈ closed: continue
        closed ← closed ∪ {n}
        if n = goal: return reconstruct(parent, goal)
        for m in neighbours(n):
            g' ← g[n] + cost(m)
            if g' < g[m]:  g[m] ← g';  parent[m] ← n;  push (g' + h(m), m)
    return failure
```

## 5.2 Adapting to a changing environment

The agent does not compute one path and follow it blindly. Every step it advances the world (`env.tick`) and re-checks its plan. Permanent and temporary changes are handled differently:

- **Permanent changes (collapsed tiles, a closed door).** The *entire remaining path* is checked each step. If any cell has become a wall, the agent replans with A\* from its **current position** (not from the start). Checking the whole path rather than only the next cell stops the agent from walking into a corridor that has already been cut off further ahead.
- **Temporary changes (moving guards).** A guard only matters when it occupies the agent's next cell. Two strategies were compared:
  - `replan` (baseline): treat the guard as a wall and replan immediately.
  - `wait_or_detour`: compute the best detour around the guard and compare it with the route that ignores the guard. If the detour costs at most 6 extra, take it. Otherwise wait, because the guard is likely to move on. To avoid deadlock, the agent waits at most 4 consecutive steps before taking the detour anyway.

```
NAVIGATE(start, goal):
    path ← A*(start, goal, guards ignored)
    loop each step:
        tick environment
        if any remaining cell of path is a wall:        path ← A*(current, goal); replans += 1
        if guard in next cell:
            detour ← A*(current, goal, guards as walls)
            if cost(detour) − cost(path) ≤ 6 or waited ≥ 4: path ← detour; replans += 1
            else: wait; continue
        move one cell
```

## 5.3 Results

Each run is a full escape (S → K → T, door opens, → E). Every configuration was run with 30 seeds; the seeds change the guards' starting positions and directions. The "random" world uses 30 generated levels (Section 4.4). The tables report means. *Cost / opt.* is the path cost divided by the static optimum, i.e. the cheapest possible escape if nothing moved.

**Table 5.1 Algorithm comparison (`wait_or_detour` strategy)**

| World | Algorithm | Success | Steps | Path cost | Cost / opt. | Nodes expanded |
|---|---|---|---|---|---|---|
| L1 (static) | BFS | 100% | 52.0 | 64.0 | 1.03 | 198 |
| | Dijkstra | 100% | 56.0 | 62.0 | 1.00 | 193 |
| | Greedy | 100% | 56.0 | 68.0 | 1.10 | 65 |
| | **A\*** | 100% | 56.0 | **62.0** | **1.00** | **128** |
| L2 | BFS | 100% | 101.7 | 104.3 | 1.45 | 1253 |
| | Dijkstra | 100% | 102.9 | 100.5 | 1.40 | 1012 |
| | Greedy | 100% | 110.1 | 114.0 | 1.58 | 154 |
| | **A\*** | 100% | 102.9 | **100.5** | 1.40 | **678** |
| L3 | BFS | 100% | 198.9 | 201.0 | 2.31 | 3906 |
| | Dijkstra | 100% | 203.9 | 198.0 | 2.28 | 3743 |
| | Greedy | 100% | 201.9 | 198.0 | 2.28 | 1560 |
| | **A\*** | 100% | **126.0** | **126.1** | **1.45** | **836** |
| Random (30 maps) | BFS | 100% | 44.6 | 50.7 | 1.23 | 491 |
| | Dijkstra | 100% | 44.4 | 47.7 | 1.16 | 464 |
| | Greedy | 100% | 46.4 | 53.1 | 1.29 | 80 |
| | **A\*** | 100% | 43.8 | **47.1** | **1.15** | **164** |

**Table 5.2 Effect of the guard strategy (A\*)**

| World | Strategy | Steps | Replans | Waits | Nodes expanded |
|---|---|---|---|---|---|
| L2 | replan | 137.7 | 9.2 | 0.0 | 804 |
| L2 | wait_or_detour | **102.9** | **4.1** | 2.4 | **678** |
| L3 | replan | 180.3 | 21.0 | 0.9 | 2566 |
| L3 | wait_or_detour | **126.0** | **2.4** | 5.9 | **836** |

*(Insert `results/nodes_expanded.png`, `results/cost_ratio.png` and `results/strategy_comparison.png`.)*

## 5.4 Discussion

- **A\* is optimal and efficient.** On the static level, A\* matches Dijkstra's optimal cost (62) while expanding 34% fewer nodes (128 vs 193). On the random maps it expands about 65% fewer nodes than Dijkstra (164 vs 464) for the same cost. The Manhattan heuristic focuses the search towards the goal.
- **Greedy is fast but not optimal.** It expands the fewest nodes (65 on Level 1) but returns paths up to 10% more expensive on Level 1 and 29% on the random maps, because it ignores the cost already paid. For example, it walks through mud whenever that looks closer to the goal.
- **BFS minimises steps, not cost.** On Level 1 BFS finds a shorter route in steps (52 vs 56) but a more expensive one in cost (64 vs 62), because it treats mud like floor. This is why cost-aware search is needed when terrain has different costs.
- **Adaptation matters.** All four algorithms reached 100% success under `wait_or_detour`, despite collapses and moving guards. Treating every guard as a wall (`replan`) made A\* take 34–43% more steps on the dynamic levels and replan up to 9× as often (21.0 vs 2.4 on Level 3). The agent kept abandoning good routes for long detours around a guard that was about to move. Greedy with `replan` failed in 10% of Level 3 runs, while every algorithm succeeded under `wait_or_detour`.
- **Limitation.** On Level 3 the uninformed algorithms (and Greedy) route through a single-width corridor patrolled by a guard. Waiting does not help there, because the guard can never step aside. They spend about 18 steps waiting before detouring, which explains their higher cost ratio (~2.3). A\* picks a route that avoids this corridor. Possible improvements: predict guard positions from their patrol pattern (space-time A\*), use incremental replanning (D\* Lite) to reduce replanning cost, or use fuzzy logic to make the wait-or-detour decision from distance and guard direction.
