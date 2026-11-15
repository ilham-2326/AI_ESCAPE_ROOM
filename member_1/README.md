# Member 1: Environment & Dynamics

The grid-world escape room: maps, walls, costs, the door, and the dynamic events (moving guards, collapsing tiles, puzzle rule changes).

## Files

| File | Purpose |
|---|---|
| `environment.py` | The `Environment` class, `Event` dataclass, `load_level(n, seed)` |
| `levels/level1.txt`, `level2.txt`, `level3.txt` | Easy, medium and hard maps |
| `levels/events.py` | When and where each level's dynamic events happen |
| `level_generator.py` | `random_level(seed)`: unlimited always-solvable rooms for experiments |
| `demo_environment.py` | Terminal demo, no Pygame needed |
| `tests/test_environment.py` | 46 pytest tests |
| `REPORT_SECTION.md` | Draft of the "Environment Design" report section |

## Run

```bash
python demo_environment.py              # print all levels + event schedules
python demo_environment.py --play 3     # animate level 3's guards and collapse
python level_generator.py               # print 3 random rooms
pytest tests                            # run the tests
```

Requires Python 3.10+ and pytest. No other dependencies.

## API for other members (do not rename)

```python
from environment import load_level, Environment

env = load_level(2, seed=0)        # seed 0 = map as drawn; other seeds randomise guards
env.start, env.key_pos, env.terminal_pos, env.door_pos, env.exit   # (row, col)
env.neighbors(p)        # free 4-neighbours of p right now
env.is_blocked(p)       # wall, closed door, guard, or out of bounds
env.is_wall(p)          # walls / closed door only (ignores guards)
env.cost(p)             # 1 floor, 3 mud
env.obstacle_adjacent(p)
env.door_open = True    # Member 4 sets this when the CSP is solved
events = env.tick(step, agent_pos)   # call once per step: 1, 2, 3, ...
env.reset()
env.get_state_for_gui() # snapshot for Member 4's renderer
env.event_schedule()    # when events fire, for Members 4 and 5
```

### Event kinds returned by `tick()`

| `kind` | `data` | Who reacts |
|---|---|---|
| `obstacle_moved` | `{"id", "from", "pos"}` | Search (wait or detour) |
| `route_blocked` | `{"cells": [...]}` | Search (replan) |
| `rule_changed` | `{}` | Member 3 (CSP) and Member 4 (FSM RESOLVE state) |

## Levels

| Level | Size | Dynamics | Event steps |
|---|---|---|---|
| 1 Easy | 11×15 | none (baseline) | none |
| 2 Medium | 14×20 | 1 guard in the hall to the terminal; the short route to the key collapses | collapse at step 8 |
| 3 Hard | 19×20 | 2 guards, the obvious route collapses, mud on the detour, puzzle rules change | collapse at step 6, rule change at step 70 |

## Design rules

- **Positions** are `(row, col)` everywhere, with 4-directional movement.
- **Guards are not walls.** The `M` cell is converted to floor when the map loads. A guard blocks only the cell it is currently on.
- **Guard movement:** a guard moves exactly 1 cell per tick along its patrol loop. If the agent or another guard is in the way, it turns around. It never jumps or walks through anyone.
- **Collapses:** a tile never collapses under the agent. The collapse is delayed until the agent steps off.
- **Reproducibility:** all randomness uses `random.Random(seed)`, so the same seed always gives the same run.
- **Input checks:** bad maps (missing or duplicate S/K/T/D/E, ragged rows, unknown symbols, patrols through walls or jumping cells) raise `LevelError` with a clear message.
- **Generated levels** are guaranteed to be:
  - solvable, with the exit reachable only through the door;
  - never fully cut off by the guard;
  - still solvable after the collapse.

## Adding a new level

1. Draw `levels/level4.txt` using the symbols in `environment.py`. Every row must be the same width. Use exactly one each of S, K, T, D and E.
2. Add `4: {...}` to `LEVEL_EVENTS` in `levels/events.py`. A patrol's first cell must be the guard's `M` position, and consecutive patrol cells must be adjacent.
3. Load it with `load_level(4)`, then run `pytest`.
# AI_ESCAPE_ROOM
# AI_ESCAPE_ROOM
