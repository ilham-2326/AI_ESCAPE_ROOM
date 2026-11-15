"""
level_generator.py  -  Member 1: random escape rooms for experiments

random_level(seed) builds a new, always-solvable escape room so Member 5 can
evaluate on many maps instead of only the 3 hand-made levels.

Guarantees for every generated level
  * S -> K -> T -> D -> E is reachable (door open for the last leg)
  * the exit is enclosed: the ONLY way in is through the door
  * the guard's patrol never cuts the map in half - there is always a
    guard-free route, so the agent can never be trapped forever
  * the collapsing tile lies on the shortest S -> K route (so it really
    forces a replan) but the room stays solvable after it collapses
  * same seed -> same level
"""

from __future__ import annotations

import random
from collections import deque

from environment import Environment

DIRS = ((-1, 0), (1, 0), (0, -1), (0, 1))


def _bfs(grid, start, blocked=frozenset()):
    """Shortest-step BFS on a char grid. Returns parent dict."""
    h, w = len(grid), len(grid[0])
    parent = {start: None}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in DIRS:
            n = (r + dr, c + dc)
            if (0 <= n[0] < h and 0 <= n[1] < w and n not in parent
                    and grid[n[0]][n[1]] != "#" and n not in blocked):
                parent[n] = (r, c)
                q.append(n)
    return parent


def _connected(grid, points, blocked=frozenset()):
    reach = _bfs(grid, points[0], blocked)
    return all(p in reach for p in points)


def _path(grid, a, b):
    parent = _bfs(grid, a)
    if b not in parent:
        return None
    p = [b]
    while parent[p[-1]] is not None:
        p.append(parent[p[-1]])
    return p[::-1]


def random_level(seed: int, height: int = 16, width: int = 20,
                 wall_density: float = 0.22, mud_density: float = 0.08,
                 max_tries: int = 500) -> Environment:
    rng = random.Random(seed)
    for _ in range(max_tries):
        g = [["#"] * width for _ in range(height)]
        for r in range(1, height - 1):
            for c in range(1, width - 1):
                g[r][c] = "#" if rng.random() < wall_density else "."

        free = [(r, c) for r in range(1, height - 1)
                for c in range(1, width - 1) if g[r][c] == "."]
        if len(free) < 40:
            continue

        # --- exit enclosed by walls, one door -------------------------------
        e = rng.choice(free)
        nbrs = [(e[0] + dr, e[1] + dc) for dr, dc in DIRS]
        inner = [n for n in nbrs if 0 < n[0] < height - 1 and 0 < n[1] < width - 1]
        if not inner:
            continue
        d = rng.choice(inner)
        for n in nbrs:
            g[n[0]][n[1]] = "#"
        g[e[0]][e[1]], g[d[0]][d[1]] = "E", "D"

        free = [(r, c) for r in range(1, height - 1)
                for c in range(1, width - 1) if g[r][c] == "."]
        if len(free) < 30:
            continue
        s, k, t = rng.sample(free, 3)
        g[s[0]][s[1]], g[k[0]][k[1]], g[t[0]][t[1]] = "S", "K", "T"

        if not _connected(g, [s, k, t, d, e]):
            continue

        # --- mud ------------------------------------------------------------
        for (r, c) in free:
            if g[r][c] == "." and rng.random() < mud_density:
                g[r][c] = "~"

        events: dict = {}

        # --- one guard on a horizontal run of >= 4 floor cells ---------------
        runs = []
        for r in range(1, height - 1):
            c = 1
            while c < width - 1:
                if g[r][c] == ".":
                    c0 = c
                    while c < width - 1 and g[r][c] == ".":
                        c += 1
                    if c - c0 >= 4:
                        runs.append([(r, x) for x in range(c0, c)])
                else:
                    c += 1
        rng.shuffle(runs)
        for run in runs:
            run = run[:rng.randint(4, min(8, len(run)))]
            if _connected(g, [s, k, t, d, e], blocked=frozenset(run)):
                r0, c0 = run[0]
                g[r0][c0] = "M"
                events["obstacle_patrol"] = {"M1": run + run[-2:0:-1]}
                break

        # --- collapse a cell on the shortest S -> K route --------------------
        sk = _path(g, s, k)
        patrol = set(events.get("obstacle_patrol", {}).get("M1", []))
        cand = [p for p in (sk or [])[2:-1]
                if g[p[0]][p[1]] in (".", "~") and p not in patrol]
        rng.shuffle(cand)
        for p in cand:
            if _connected(g, [s, k, t, d, e], blocked=frozenset({p})):
                g[p[0]][p[1]] = "C"
                events["collapse"] = {"step": rng.randint(2, max(2, len(sk) // 2)),
                                      "cells": [p]}
                break

        # --- puzzle rule change for the CSP / FSM modules -------------------
        events["rule_change"] = {"step": rng.randint(30, 60)}

        rows = ["".join(r) for r in g]
        return Environment(grid_rows=rows, events=events, seed=seed)

    raise RuntimeError(f"Could not generate a level for seed {seed}")


if __name__ == "__main__":
    for sd in (1, 2, 3):
        env = random_level(sd)
        print(f"seed {sd}: {env.event_schedule()}")
        env.print_grid()
        print()
