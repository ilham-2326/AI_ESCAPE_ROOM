"""Tests for Member 1's environment.  Run:  pytest member_1/tests"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from environment import Environment, LevelError, load_level   # noqa: E402
from level_generator import random_level, _connected          # noqa: E402

TINY = ["#######",
        "#S.~K.#",
        "#.###.#",
        "#T.C.D#",
        "#####E#"]


def tiny(events=None, seed=0):
    return Environment(grid_rows=TINY, events=events or {}, seed=seed)


# ---------------------------------------------------------------- loading
@pytest.mark.parametrize("lv", [1, 2, 3])
def test_levels_load(lv):
    env = load_level(lv)
    for p in (env.start, env.key_pos, env.terminal_pos, env.door_pos, env.exit):
        assert env.in_bounds(p)


def test_positions_are_row_col():
    env = tiny()
    assert env.start == (1, 1) and env.key_pos == (1, 4)
    assert env.terminal_pos == (3, 1) and env.door_pos == (3, 5)


def test_missing_symbol_raises():
    with pytest.raises(LevelError):
        Environment(grid_rows=["####", "#S.#", "####"])


def test_ragged_rows_raise():
    rows = list(TINY)
    rows[1] = rows[1] + "."
    with pytest.raises(LevelError):
        Environment(grid_rows=rows)


def test_unknown_symbol_raises():
    rows = list(TINY)
    rows[1] = "#S.?K.#"
    with pytest.raises(LevelError):
        Environment(grid_rows=rows)


# ---------------------------------------------------------------- core API
def test_neighbors_and_walls():
    env = tiny()
    assert sorted(env.neighbors(env.start)) == [(1, 2), (2, 1)]
    assert env.is_blocked((0, 0))
    assert env.is_blocked((-1, 3))            # out of bounds


def test_costs():
    env = tiny()
    assert env.cost((1, 2)) == 1
    assert env.cost((1, 3)) == 3              # mud


def test_door_blocks_until_open():
    env = tiny()
    assert env.is_blocked(env.door_pos)
    env.door_open = True
    assert not env.is_blocked(env.door_pos)


# ---------------------------------------------------------------- dynamics
def test_collapse_fires_on_schedule():
    env = tiny({"collapse": {"step": 3, "cells": [(3, 3)]}})
    assert env.tick(1) == [] and env.tick(2) == []
    ev = env.tick(3)
    assert [e.kind for e in ev] == ["route_blocked"]
    assert env.is_blocked((3, 3))


def test_collapse_waits_until_agent_leaves():
    env = tiny({"collapse": {"step": 1, "cells": [(3, 3)]}})
    assert env.tick(1, agent_pos=(3, 3)) == []
    assert not env.is_blocked((3, 3))
    ev = env.tick(2, agent_pos=(3, 2))
    assert ev and env.is_blocked((3, 3))


def test_rule_change_event():
    env = tiny({"rule_change": {"step": 2}})
    assert [e.kind for e in env.tick(2)] == ["rule_changed"]


def test_obstacle_patrol_moves_one_cell_per_tick():
    env = load_level(2)
    prev = env.obstacles["M1"]
    for s in range(1, 30):
        env.tick(s)
        cur = env.obstacles["M1"]
        assert abs(cur[0] - prev[0]) + abs(cur[1] - prev[1]) <= 1
        prev = cur


def test_obstacle_never_moves_onto_agent():
    env = load_level(2)
    for s in range(1, 60):
        agent = (9, 7)
        env.tick(s, agent_pos=agent)
        assert env.obstacles["M1"] != agent


def test_obstacle_is_not_a_wall():
    env = load_level(2)
    start_cell = env.obstacles["M1"]
    assert env.is_blocked(start_cell)         # occupied now
    env.tick(1)
    assert not env.is_blocked(start_cell)     # free once the guard moved
    assert not env.is_wall(start_cell)


def test_bad_patrol_rejected():
    rows = ["#######", "#S.~K.#", "#.###.#", "#TMC.D#", "#####E#"]
    with pytest.raises(LevelError):            # jumps two cells
        Environment(grid_rows=rows,
                    events={"obstacle_patrol": {"M1": [(3, 2), (3, 4)]}})


# ---------------------------------------------------------------- reproducibility
@pytest.mark.parametrize("lv", [2, 3])
def test_same_seed_same_run(lv):
    def run(seed):
        env = load_level(lv, seed=seed)
        trace = []
        for s in range(1, 50):
            env.tick(s)
            trace.append(tuple(sorted(env.obstacles.items())))
        return trace
    assert run(7) == run(7)


def test_reset_restores_level():
    env = load_level(3)
    for s in range(1, 20):
        env.tick(s)
    env.door_open = True
    env.reset()
    fresh = load_level(3)
    assert env.get_state_for_gui() == fresh.get_state_for_gui()


# ---------------------------------------------------------------- generator
@pytest.mark.parametrize("seed", range(1, 26))
def test_random_levels_solvable(seed):
    env = random_level(seed)
    g = env._rows
    pts = [env.start, env.key_pos, env.terminal_pos, env.door_pos, env.exit]
    assert _connected(g, pts)
    # exit only reachable through the door
    assert not _connected(g, [env.start, env.exit], blocked=frozenset({env.door_pos}))
    # still solvable after the collapse
    cells = env._events_cfg.get("collapse", {}).get("cells", [])
    assert _connected(g, pts, blocked=frozenset(map(tuple, cells)))


def test_random_level_reproducible():
    assert random_level(5)._rows == random_level(5)._rows
