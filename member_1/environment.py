"""
environment.py  -  Member 1: Environment & Dynamics
CSCI218 Group Project - AI Escape Room

Grid-world escape room with dynamic elements:
  * moving obstacles that patrol a fixed loop
  * collapsible tiles that turn into walls at a scheduled step
  * a puzzle "rule change" event (consumed by the CSP / FSM modules)

Conventions (agreed with the whole team):
  * positions are (row, col) tuples
  * 4-directional movement, no diagonals
  * the map .txt file is the single source of truth for a level

Map symbols
  #  wall                    S  start
  .  floor   (cost 1)        K  key
  ~  mud     (cost 3)        T  puzzle terminal
  C  collapsible floor       D  door (blocked until door_open = True)
  M  moving obstacle start   E  exit
"""

from __future__ import annotations

import copy
import os
import random
from dataclasses import dataclass, field

# --------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------
WALL, FLOOR, MUD, COLLAPSE, OBSTACLE = "#", ".", "~", "C", "M"
START, KEY, TERMINAL, DOOR, EXIT = "S", "K", "T", "D", "E"

COST = {FLOOR: 1, MUD: 3, COLLAPSE: 1, START: 1, KEY: 1,
        TERMINAL: 1, DOOR: 1, EXIT: 1}

SPECIAL = (START, KEY, TERMINAL, DOOR, EXIT)
VALID_SYMBOLS = set(COST) | {WALL, OBSTACLE}

LEVEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "levels")


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------
@dataclass
class Event:
    """Something that changed in the world during tick().

    kind:
      "obstacle_moved" -> data = {"id": "M1", "from": (r,c), "pos": (r,c)}
      "route_blocked"  -> data = {"cells": [(r,c), ...]}
      "rule_changed"   -> data = {}            (handled by CSP / FSM)
    """
    kind: str
    step: int
    data: dict = field(default_factory=dict)


class LevelError(ValueError):
    """Raised when a map or its event config is invalid."""


# --------------------------------------------------------------------------
# Environment
# --------------------------------------------------------------------------
class Environment:
    """Grid world used by the search, CSP and agent modules.

    Public API (do NOT rename - other members depend on it):
        neighbors(p) -> list[(r,c)]
        is_blocked(p) -> bool
        cost(p) -> int
        tick(step, agent_pos=None) -> list[Event]
        reset()
        door_open  (bool attribute)
        start, key_pos, terminal_pos, door_pos, exit
        obstacles  (dict id -> (r,c))
    """

    def __init__(self, map_path: str | None = None, events: dict | None = None,
                 seed: int = 0, grid_rows: list[str] | None = None):
        if map_path is None and grid_rows is None:
            raise LevelError("Give either map_path or grid_rows")
        if grid_rows is None:
            with open(map_path, encoding="utf-8") as f:
                grid_rows = [ln.rstrip("\n\r") for ln in f if ln.strip()]
        self._rows = list(grid_rows)
        self._events_cfg = copy.deepcopy(events or {})
        self.seed = seed
        self.map_path = map_path
        self.reset()

    # ------------------------------------------------------------------ setup
    def reset(self) -> None:
        """Restore the level to step 0 (same seed -> identical run)."""
        self.rng = random.Random(self.seed)
        self.grid = [list(r) for r in self._rows]
        self.h, self.w = len(self.grid), len(self.grid[0])
        self.door_open = False
        self.step = 0
        self.obstacles: dict[str, tuple] = {}
        self.event_log: list[Event] = []
        self._pending_collapse: set = set()

        found = {s: [] for s in SPECIAL}
        for r, row in enumerate(self.grid):
            if len(row) != self.w:
                raise LevelError(f"Row {r} has length {len(row)}, expected {self.w}")
            for c, ch in enumerate(row):
                if ch not in VALID_SYMBOLS:
                    raise LevelError(f"Unknown symbol {ch!r} at {(r, c)}")
                if ch in found:
                    found[ch].append((r, c))
                elif ch == OBSTACLE:
                    oid = f"M{len(self.obstacles) + 1}"
                    self.obstacles[oid] = (r, c)
                    self.grid[r][c] = FLOOR          # obstacle is NOT a wall

        for sym, cells in found.items():
            if len(cells) != 1:
                raise LevelError(f"Map needs exactly one {sym!r}, found {len(cells)}")

        self.start = found[START][0]
        self.key_pos = found[KEY][0]
        self.terminal_pos = found[TERMINAL][0]
        self.door_pos = found[DOOR][0]
        self.exit = found[EXIT][0]

        self._validate_events()
        patrols = self._events_cfg.get("obstacle_patrol", {})
        self._patrol_idx = {oid: 0 for oid in patrols}
        self._patrol_dir = {oid: 1 for oid in patrols}
        # seed 0 = the exact map as drawn. Any other seed randomises where
        # each guard starts on its loop and which way it walks, so repeated
        # trials (Member 5) see different - but reproducible - dynamics.
        if self.seed != 0:
            for oid, route in patrols.items():
                i = self.rng.randrange(len(route))
                self._patrol_idx[oid] = i
                self._patrol_dir[oid] = self.rng.choice((1, -1))
                self.obstacles[oid] = tuple(route[i])

    def _validate_events(self) -> None:
        patrols = self._events_cfg.get("obstacle_patrol", {})
        for oid, route in patrols.items():
            if oid not in self.obstacles:
                raise LevelError(f"Patrol for unknown obstacle {oid}")
            if tuple(route[0]) != self.obstacles[oid]:
                raise LevelError(f"{oid} patrol must start at its map position "
                                 f"{self.obstacles[oid]}, got {route[0]}")
            for i, p in enumerate(route):
                p = tuple(p)
                ch = self.grid[p[0]][p[1]]
                if ch in (WALL,) + SPECIAL:
                    raise LevelError(f"{oid} patrol cell {p} is on {ch!r}")
                nxt = tuple(route[(i + 1) % len(route)])
                if abs(p[0] - nxt[0]) + abs(p[1] - nxt[1]) > 1:
                    raise LevelError(f"{oid} patrol jumps from {p} to {nxt}")
        col = self._events_cfg.get("collapse")
        if col:
            for (r, c) in col["cells"]:
                if self.grid[r][c] != COLLAPSE:
                    raise LevelError(f"Collapse cell {(r, c)} is not marked 'C'")

    # ------------------------------------------------------------ core API
    def in_bounds(self, p) -> bool:
        return 0 <= p[0] < self.h and 0 <= p[1] < self.w

    def is_wall(self, p) -> bool:
        """Static blockage only (walls, closed door) - ignores obstacles."""
        ch = self.grid[p[0]][p[1]]
        return ch == WALL or (ch == DOOR and not self.door_open)

    def is_blocked(self, p) -> bool:
        """True if the agent cannot stand on p right now."""
        if not self.in_bounds(p):
            return True
        return self.is_wall(p) or p in self.obstacles.values()

    def neighbors(self, p) -> list:
        r, c = p
        return [q for q in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if not self.is_blocked(q)]

    def cost(self, p) -> int:
        return COST.get(self.grid[p[0]][p[1]], 1)

    def obstacle_adjacent(self, p) -> bool:
        """True if p is next to (or on) a moving obstacle - used by
        search.py's avoid_obstacles variant."""
        return any(abs(p[0] - o[0]) + abs(p[1] - o[1]) <= 1
                   for o in self.obstacles.values())

    # ------------------------------------------------------------- dynamics
    def tick(self, step: int, agent_pos=None) -> list[Event]:
        """Advance the world to `step` and return the events that fired.

        Call it exactly once per simulation step, with step = 1, 2, 3, ...

        agent_pos (optional) lets the world respect two safety rules:
          * an obstacle never moves onto the agent - it turns around
          * a tile never collapses under the agent - it collapses as soon
            as the agent leaves it
        """
        self.step = step
        fired: list[Event] = []
        agent_pos = tuple(agent_pos) if agent_pos is not None else None

        # 1. moving obstacles advance one cell along their patrol loop.
        #    If the next cell holds the agent (or another obstacle) the guard
        #    turns around instead - it never jumps or walks through anyone.
        for oid, route in self._events_cfg.get("obstacle_patrol", {}).items():
            old = self.obstacles[oid]
            idx, d = self._patrol_idx[oid], self._patrol_dir[oid]
            occupied = {agent_pos} | {p for k, p in self.obstacles.items() if k != oid}
            nxt = (idx + d) % len(route)
            if tuple(route[nxt]) in occupied:
                d = -d
                nxt = (idx + d) % len(route)
                self._patrol_dir[oid] = d
                if tuple(route[nxt]) in occupied:
                    continue                  # boxed in - stay this step
            self._patrol_idx[oid] = nxt
            new = tuple(route[nxt])
            if new == old:
                continue
            self.obstacles[oid] = new
            fired.append(Event("obstacle_moved", step,
                               {"id": oid, "from": old, "pos": new}))

        # 2. scheduled collapse (+ any collapse delayed by the agent)
        col = self._events_cfg.get("collapse")
        if col and step == col["step"]:
            self._pending_collapse |= {tuple(c) for c in col["cells"]}
        if self._pending_collapse:
            now = [c for c in self._pending_collapse if c != agent_pos]
            for (r, c) in now:
                self.grid[r][c] = WALL
                self._pending_collapse.discard((r, c))
            if now:
                fired.append(Event("route_blocked", step, {"cells": sorted(now)}))

        # 3. puzzle rule change (Member 3 / 4 decide what it means)
        rc = self._events_cfg.get("rule_change")
        if rc and step == rc["step"]:
            fired.append(Event("rule_changed", step, {}))

        self.event_log.extend(fired)
        return fired

    def event_schedule(self) -> dict:
        """Summary of when events fire - handy for Members 4 and 5."""
        cfg = self._events_cfg
        return {
            "collapse_step": cfg.get("collapse", {}).get("step"),
            "collapse_cells": cfg.get("collapse", {}).get("cells", []),
            "rule_change_step": cfg.get("rule_change", {}).get("step"),
            "moving_obstacles": list(cfg.get("obstacle_patrol", {}).keys()),
        }

    # ---------------------------------------------------------- GUI / debug
    def get_state_for_gui(self) -> dict:
        """Read-only snapshot for Member 4's renderer."""
        return {
            "grid": ["".join(r) for r in self.grid],
            "obstacles": dict(self.obstacles),
            "door_open": self.door_open,
            "step": self.step,
            "start": self.start, "key": self.key_pos,
            "terminal": self.terminal_pos, "door": self.door_pos,
            "exit": self.exit,
        }

    def render(self, path=None, agent=None) -> str:
        """ASCII picture of the world. Path cells shown as '*', agent 'A',
        obstacles 'M'."""
        path = set(path or [])
        obs = set(self.obstacles.values())
        out = []
        for r in range(self.h):
            line = []
            for c in range(self.w):
                p = (r, c)
                ch = self.grid[r][c]
                if p == agent:
                    ch = "A"
                elif p in obs:
                    ch = "M"
                elif p in path and ch in (FLOOR, MUD, COLLAPSE):
                    ch = "*"
                elif ch == DOOR and self.door_open:
                    ch = "d"
                line.append(ch)
            out.append("".join(line))
        return "\n".join(out)

    def print_grid(self, path=None, agent=None) -> None:
        print(self.render(path, agent))

    def __repr__(self):
        return (f"Environment({self.h}x{self.w}, step={self.step}, "
                f"obstacles={self.obstacles}, door_open={self.door_open})")


# --------------------------------------------------------------------------
# Level loading helpers
# --------------------------------------------------------------------------
def load_level(level: int, seed: int = 0) -> Environment:
    """load_level(1..3) -> Environment with that level's map and events."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "level_events", os.path.join(LEVEL_DIR, "events.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    LEVEL_EVENTS = mod.LEVEL_EVENTS
    path = os.path.join(LEVEL_DIR, f"level{level}.txt")
    if not os.path.exists(path):
        raise LevelError(f"No such level file: {path}")
    return Environment(path, LEVEL_EVENTS.get(level, {}), seed=seed)
