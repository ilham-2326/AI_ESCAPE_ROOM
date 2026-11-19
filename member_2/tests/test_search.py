"""Tests for Member 2's search module.  Run:  pytest member_2/tests

Uses Member 1's environment. Looks for it in ../member_1 (two-folder
layout) or alongside search.py (merged repo layout).
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
M2 = os.path.dirname(HERE)
sys.path[:0] = [M2, os.path.join(os.path.dirname(M2), "member_1")]

from environment import Environment, load_level                  # noqa: E402
from level_generator import random_level                         # noqa: E402
from search import (ALGORITHMS, manhattan, navigate, path_cost,  # noqa: E402
                    path_still_valid, plan, zero)

LEVELS = [1, 2, 3]


def open_room(rows):
    return Environment(grid_rows=rows)


def path_is_legal(env, path):
    for a, b in zip(path, path[1:]):
        assert manhattan(a, b) == 1, f"jump {a}->{b}"
    assert all(not env.is_blocked(p) for p in path), "path through a blocked cell"


# ------------------------------------------------------------ correctness
@pytest.mark.parametrize("lv", LEVELS)
@pytest.mark.parametrize("algo", ALGORITHMS)
def test_every_algorithm_finds_legal_path(lv, algo):
    env = load_level(lv)
    path, st = plan(env, env.start, env.key_pos, algo)
    assert path[0] == env.start and path[-1] == env.key_pos
    path_is_legal(env, path)
    assert st["found"] and st["path_cost"] == path_cost(env, path)


@pytest.mark.parametrize("lv", LEVELS)
def test_astar_matches_dijkstra_cost(lv):
    env = load_level(lv)
    env.door_open = True
    for goal in (env.key_pos, env.terminal_pos, env.exit):
        _, a = plan(env, env.start, goal, "astar")
        _, d = plan(env, env.start, goal, "dijkstra")
        assert a["path_cost"] == d["path_cost"]


@pytest.mark.parametrize("lv", LEVELS)
def test_astar_expands_no_more_than_dijkstra(lv):
    env = load_level(lv)
    _, a = plan(env, env.start, env.key_pos, "astar")
    _, d = plan(env, env.start, env.key_pos, "dijkstra")
    assert a["nodes_expanded"] <= d["nodes_expanded"]


@pytest.mark.parametrize("lv", LEVELS)
def test_greedy_never_beats_astar(lv):
    env = load_level(lv)
    _, a = plan(env, env.start, env.key_pos, "astar")
    _, g = plan(env, env.start, env.key_pos, "greedy")
    assert g["path_cost"] >= a["path_cost"]


@pytest.mark.parametrize("lv", LEVELS)
def test_bfs_gives_fewest_steps(lv):
    env = load_level(lv)
    _, b = plan(env, env.start, env.key_pos, "bfs")
    for algo in ("dijkstra", "greedy", "astar"):
        _, o = plan(env, env.start, env.key_pos, algo)
        assert b["path_length"] <= o["path_length"]


def test_astar_avoids_mud_bfs_does_not():
    rows = ["#######",
            "#S~~~E#",
            "#.....#",
            "##D#K##",
            "##T####"]
    # (exit not enclosed here - we only test path choice S -> E)
    env = open_room(rows)
    pb, sb = plan(env, env.start, env.exit, "bfs")
    pa, sa = plan(env, env.start, env.exit, "astar")
    assert sb["path_length"] == 4 and sb["path_cost"] == 10   # straight through mud
    assert sa["path_cost"] == 6                                 # around the mud
    assert sa["path_cost"] < sb["path_cost"]


def test_zero_heuristic_equals_dijkstra():
    env = load_level(3)
    _, a0 = plan(env, env.start, env.key_pos, "astar", heuristic=zero)
    _, d = plan(env, env.start, env.key_pos, "dijkstra")
    assert a0["path_cost"] == d["path_cost"]


def test_heuristic_is_admissible_on_every_cell():
    env = load_level(3)
    goal = env.key_pos
    for r in range(env.h):
        for c in range(env.w):
            if not env.is_blocked((r, c)):
                p, st = plan(env, (r, c), goal, "dijkstra")
                if p:
                    assert manhattan((r, c), goal) <= st["path_cost"]


# ------------------------------------------------------------ edge cases
@pytest.mark.parametrize("algo", ALGORITHMS)
def test_no_path_returns_none(algo):
    env = load_level(1)                 # door closed -> exit unreachable
    path, st = plan(env, env.start, env.exit, algo)
    assert path is None and not st["found"] and st["path_cost"] is None


@pytest.mark.parametrize("algo", ALGORITHMS)
def test_start_equals_goal(algo):
    env = load_level(1)
    path, st = plan(env, env.start, env.start, algo)
    assert path == [env.start] and st["path_cost"] == 0


def test_bad_algorithm_name():
    env = load_level(1)
    with pytest.raises(ValueError):
        plan(env, env.start, env.key_pos, "dfs")


def test_return_explored():
    env = load_level(1)
    path, st, explored = plan(env, env.start, env.key_pos, "astar",
                              return_explored=True)
    assert len(explored) == st["nodes_expanded"]
    assert set(path) <= explored | {env.key_pos}


# ------------------------------------------------------------ replanning
def test_path_still_valid_detects_collapse():
    env = load_level(2)
    path, _ = plan(env, env.start, env.key_pos)
    assert path_still_valid(env, path)
    for s in range(1, 9):
        env.tick(s)                     # collapse fires at step 8
    assert path_still_valid(env, path) == ((5, 9) not in path)


def test_ignore_obstacles_plans_through_guard():
    env = load_level(2)
    guard = env.obstacles["M1"]
    p_dyn, _ = plan(env, (9, 4), (9, 6))
    p_ign, _ = plan(env, (9, 4), (9, 6), ignore_obstacles=True)
    assert guard not in p_dyn
    assert guard in p_ign


def test_avoid_obstacles_keeps_distance():
    env = load_level(2)
    p_plain, _ = plan(env, (10, 4), (10, 10))
    p_avoid, _ = plan(env, (10, 4), (10, 10), avoid_obstacles=True)
    near = lambda p: sum(env.obstacle_adjacent(c) for c in p)
    assert near(p_avoid) <= near(p_plain)


@pytest.mark.parametrize("strategy", ["replan", "wait_or_detour"])
@pytest.mark.parametrize("lv", LEVELS)
def test_full_escape_all_levels(lv, strategy):
    env = load_level(lv)
    step, pos = 0, env.start
    for i, goal in enumerate((env.key_pos, env.terminal_pos, env.exit)):
        if i == 2:
            env.door_open = True        # the CSP solved the puzzle
        log = navigate(env, pos, goal, "astar", start_step=step,
                       obstacle_strategy=strategy)
        assert log["success"], f"leg {i} failed"
        path_is_legal_moves(log["path_taken"])
        step, pos = log["end_step"], log["end_pos"]


def path_is_legal_moves(path):
    for a, b in zip(path, path[1:]):
        assert manhattan(a, b) == 1


def test_collapse_forces_replan():
    env = load_level(2)
    log = navigate(env, env.start, env.key_pos, "astar")
    kinds = {e.kind for e in log["events"]}
    assert "route_blocked" in kinds and log["replans"] >= 1
    assert (5, 9) not in log["path_taken"]


def test_agent_never_collides_with_guard():
    env = load_level(3)
    hits = []

    def check(step, pos, path):
        if pos in env.obstacles.values():
            hits.append((step, pos))

    env.door_open = True
    navigate(env, env.start, env.exit, "astar", on_step=check)
    assert hits == []


@pytest.mark.parametrize("seed", range(1, 21))
def test_random_levels_escape(seed):
    env = random_level(seed)
    step, pos = 0, env.start
    for i, goal in enumerate((env.key_pos, env.terminal_pos, env.exit)):
        if i == 2:
            env.door_open = True
        log = navigate(env, pos, goal, "astar", start_step=step)
        assert log["success"]
        step, pos = log["end_step"], log["end_pos"]


def test_navigate_reproducible():
    a = navigate(load_level(3, seed=4), (1, 1), (7, 18))
    b = navigate(load_level(3, seed=4), (1, 1), (7, 18))
    assert a["path_taken"] == b["path_taken"]
