"""
search.py  -  Member 2: Search & Path Planning
CSCI218 Group Project - AI Escape Room

Algorithms
  bfs       - uninformed, FIFO queue, optimal only when every step costs the same
  dijkstra  - uniform-cost search, f(n) = g(n)          (optimal, no heuristic)
  greedy    - greedy best-first, f(n) = h(n)            (fast, NOT optimal)
  astar     - A*, f(n) = g(n) + h(n)                    (optimal with admissible h)

Heuristic
  Manhattan distance. With 4-directional moves and minimum step cost 1 it
  never over-estimates the true cost -> admissible -> A* returns optimal paths.
  It is also consistent, so a node is never re-expanded once closed.

Dynamic environments
  path_still_valid()  - checks whether the rest of a planned path is still free
  navigate()          - executes a path step by step, calling env.tick() and
                        re-planning from the CURRENT position whenever the
                        remaining path becomes blocked.

This module does not import environment.py - it only needs an object with
neighbors(p), cost(p), is_blocked(p) (and optionally obstacle_adjacent(p),
tick(step, agent_pos)). That keeps the modules loosely coupled.
"""

from __future__ import annotations

import heapq
import itertools
import time
from collections import deque

ALGORITHMS = ("bfs", "dijkstra", "greedy", "astar")
OBSTACLE_PENALTY = 5          # extra cost next to a moving obstacle


# --------------------------------------------------------------------------
# Heuristics
# --------------------------------------------------------------------------
def manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def zero(a, b) -> int:          # turns A* into Dijkstra - useful for tests
    return 0


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def _reconstruct(parent: dict, goal) -> list:
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


def _neighbors(env, p, ignore_obstacles: bool):
    """Neighbours of p. With ignore_obstacles=True moving obstacles are
    treated as passable (only walls / closed door block) - used to ask
    'what would the route be if the guard stepped aside?'."""
    if not ignore_obstacles or not hasattr(env, "is_wall"):
        return env.neighbors(p)
    r, c = p
    return [q for q in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
            if env.in_bounds(q) and not env.is_wall(q)]


def _blocked(env, p, ignore_obstacles: bool) -> bool:
    if ignore_obstacles and hasattr(env, "is_wall"):
        return (not env.in_bounds(p)) or env.is_wall(p)
    return env.is_blocked(p)


def _step_cost(env, p, avoid_obstacles: bool) -> int:
    c = env.cost(p)
    if avoid_obstacles and hasattr(env, "obstacle_adjacent") and env.obstacle_adjacent(p):
        c += OBSTACLE_PENALTY
    return c


def path_cost(env, path) -> int | None:
    """Real (un-penalised) cost of a path, excluding the start cell."""
    if path is None:
        return None
    return sum(env.cost(p) for p in path[1:])


# --------------------------------------------------------------------------
# Main planner
# --------------------------------------------------------------------------
def plan(env, start, goal, algo: str = "astar", heuristic=manhattan,
         avoid_obstacles: bool = False, return_explored: bool = False,
         ignore_obstacles: bool = False):
    """Find a path from start to goal.

    Returns (path, stats)            or
            (path, stats, explored)  if return_explored=True

    path  : list of (r,c) from start to goal inclusive, or None if no path
    stats : {"algo", "nodes_expanded", "path_cost", "path_length", "time_ms",
             "found"}
    explored : set of expanded cells (for the GUI overlay)

    avoid_obstacles  : +5 cost on cells next to a moving obstacle (keeps distance)
    ignore_obstacles : plan as if moving obstacles were not there (walls only)

    nodes_expanded counts nodes POPPED and expanded (not pushed), so all
    four algorithms are compared fairly.
    """
    if algo not in ALGORITHMS:
        raise ValueError(f"algo must be one of {ALGORITHMS}, got {algo!r}")
    start, goal = tuple(start), tuple(goal)
    t0 = time.perf_counter()
    expanded = 0
    closed: set = set()
    parent = {start: None}

    if start == goal:
        found = True
    elif algo == "bfs":
        found = False
        frontier = deque([start])
        while frontier:
            cur = frontier.popleft()
            closed.add(cur)
            expanded += 1
            if cur == goal:
                found = True
                break
            for n in _neighbors(env, cur, ignore_obstacles):
                if n not in parent:
                    parent[n] = cur
                    frontier.append(n)
    else:
        found = False
        if algo == "astar":
            f = lambda g, n: g + heuristic(n, goal)
        elif algo == "dijkstra":
            f = lambda g, n: g
        else:                                   # greedy
            f = lambda g, n: heuristic(n, goal)
        tie = itertools.count()                 # stable tie-breaking (FIFO)
        g_cost = {start: 0}
        frontier = [(f(0, start), next(tie), 0, start)]
        while frontier:
            _, _, g, cur = heapq.heappop(frontier)
            if cur in closed:                   # stale duplicate entry
                continue
            closed.add(cur)
            expanded += 1
            if cur == goal:
                found = True
                break
            for n in _neighbors(env, cur, ignore_obstacles):
                if n in closed:
                    continue
                ng = g + _step_cost(env, n, avoid_obstacles)
                if ng < g_cost.get(n, float("inf")):
                    g_cost[n] = ng
                    parent[n] = cur
                    heapq.heappush(frontier, (f(ng, n), next(tie), ng, n))

    path = _reconstruct(parent, goal) if found else None
    stats = {
        "algo": algo,
        "found": found,
        "nodes_expanded": expanded,
        "path_cost": path_cost(env, path),
        "path_length": (len(path) - 1) if path else None,
        "time_ms": (time.perf_counter() - t0) * 1000,
    }
    if return_explored:
        return path, stats, closed
    return path, stats


# --------------------------------------------------------------------------
# Replanning support
# --------------------------------------------------------------------------
def path_still_valid(env, path, from_index: int = 0,
                     ignore_obstacles: bool = False) -> bool:
    """False if ANY remaining cell of the path is now blocked.

    Trigger choice (documented in the report): we check the whole remaining
    path, not just the next cell, so the agent never walks into a corridor
    that has already been cut off further ahead.
    """
    if path is None:
        return False
    return all(not _blocked(env, p, ignore_obstacles) for p in path[from_index:])


WAIT_TOLERANCE = 6     # wait for a guard if detouring costs > this much extra
MAX_PATIENCE = 4       # ...but never wait more than this many steps in a row


def navigate(env, start, goal, algo: str = "astar", start_step: int = 0,
             max_steps: int = 500, avoid_obstacles: bool = False,
             obstacle_strategy: str = "wait_or_detour",
             max_wait: int = 30, on_step=None) -> dict:
    """Move an agent from start to goal in a DYNAMIC environment.

    Two kinds of change are handled differently:

    * Permanent changes (collapsed tiles, closed door) -> whole-path check.
      If ANY remaining cell of the plan is now a wall, REPLAN from the
      agent's current position.

    * Moving obstacles (temporary) -> local decision when the guard is in
      the very next cell:
        obstacle_strategy="replan"          treat the guard as a wall and
                                            replan immediately (baseline)
        obstacle_strategy="wait_or_detour"  compare the detour with the
                                            route that ignores the guard.
                                            Detour costs <= WAIT_TOLERANCE
                                            extra -> take it; otherwise WAIT
                                            (at most MAX_PATIENCE steps, then
                                            detour anyway to avoid deadlock).

    Each step: env.tick(step, agent_pos) -> check plan -> move or wait.

    Returns a log dict:
      success, steps, end_step, end_pos, path_taken, path_cost, replans,
      waits, plans, nodes_expanded (sum over all plans), planning_time_ms,
      events
    """
    if obstacle_strategy not in ("replan", "wait_or_detour"):
        raise ValueError("obstacle_strategy must be 'replan' or 'wait_or_detour'")
    pos, goal = tuple(start), tuple(goal)
    step = start_step
    taken = [pos]
    log = {"algo": algo, "obstacle_strategy": obstacle_strategy, "replans": 0,
           "waits": 0, "plans": 0, "nodes_expanded": 0,
           "planning_time_ms": 0.0, "events": []}
    smart = obstacle_strategy == "wait_or_detour"

    def do_plan(ignore=False):
        p, st = plan(env, pos, goal, algo, avoid_obstacles=avoid_obstacles,
                     ignore_obstacles=ignore)
        log["plans"] += 1
        log["nodes_expanded"] += st["nodes_expanded"]
        log["planning_time_ms"] += st["time_ms"]
        return p

    # smart agents plan around walls and deal with guards when they meet them
    path = do_plan(ignore=smart)
    idx = 1
    consecutive_waits = 0
    patience = 0

    while pos != goal and step - start_step < max_steps:
        step += 1
        events = env.tick(step, pos) if hasattr(env, "tick") else []
        log["events"].extend(events)

        # (a) permanent change: remaining path hits a wall -> replan
        if path is None or not path_still_valid(env, path, idx, ignore_obstacles=smart):
            if path is not None:
                log["replans"] += 1
            path, idx = do_plan(ignore=smart), 1

        # (b) moving obstacle in the next cell
        if path is not None and env.is_blocked(path[idx]):
            if not smart:
                log["replans"] += 1
                path, idx = do_plan(), 1
            else:
                detour = do_plan(ignore=False)
                extra = (path_cost(env, detour) - path_cost(env, path[idx - 1:])
                         if detour else None)
                if detour and (extra <= WAIT_TOLERANCE or patience >= MAX_PATIENCE):
                    log["replans"] += 1
                    path, idx, patience = detour, 1, 0
                else:
                    patience += 1
                    log["waits"] += 1
                    consecutive_waits += 1
                    if consecutive_waits > max_wait:
                        break
                    if on_step:
                        on_step(step, pos, path)
                    continue

        if path is None:                         # no route at all right now
            log["waits"] += 1
            consecutive_waits += 1
            if consecutive_waits > max_wait:
                break
            if on_step:
                on_step(step, pos, path)
            continue

        consecutive_waits = 0
        if not env.is_blocked(path[idx]):
            patience = 0
        pos = path[idx]
        idx += 1
        taken.append(pos)
        if on_step:
            on_step(step, pos, path)

    log.update({
        "success": pos == goal,
        "steps": step - start_step,
        "end_step": step,
        "end_pos": pos,
        "path_taken": taken,
        "path_cost": path_cost(env, taken),
    })
    return log
