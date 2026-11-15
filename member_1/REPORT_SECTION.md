# 4. Environment Design

## 4.1 Representation

The escape room is a 2-D grid world. Each cell is identified by a `(row, col)` tuple, and the agent moves one cell per step in four directions (up, down, left, right). Each level is stored as a plain-text map, which is the single source of truth for that level. A separate configuration file describes the level's dynamic events, so the static layout and the dynamics can be changed independently.

| Symbol | Meaning | Step cost |
|---|---|---|
| `#` | Wall | impassable |
| `.` | Floor | 1 |
| `~` | Mud | 3 |
| `C` | Collapsible floor (becomes a wall at a scheduled step) | 1 |
| `M` | Starting cell of a moving obstacle (guard) | 1 |
| `S`, `K`, `T` | Start, key, puzzle terminal | 1 |
| `D` | Door, impassable until the puzzle is solved | 1 |
| `E` | Exit | 1 |

The two step costs (1 and 3) matter: they make *path cost* differ from *path length*. Uninformed breadth-first search minimises the number of steps, while cost-aware search (Dijkstra, A\*) minimises total cost. The exit is always enclosed by walls except for the door, so the agent must complete the full task sequence (key → terminal → puzzle → door → exit).

The `Environment` class exposes a small interface that the other modules depend on:

- `neighbors(p)`, `is_blocked(p)`, `is_wall(p)` and `cost(p)` for the search module;
- `tick(step, agent_pos)` to advance the world;
- `door_open`, set by the agent once the CSP is solved;
- `get_state_for_gui()` for the renderer.

Search depends only on this interface, not on the class itself, which keeps the modules loosely coupled.

## 4.2 Dynamic elements

`tick()` is called once per simulation step and returns a list of `Event` objects describing what changed:

1. **Moving obstacles (`obstacle_moved`).** Each guard follows a patrol loop, one cell per step. A guard is not a wall: it blocks only the cell it currently occupies. If the agent or another guard is in its way, the guard turns around rather than passing through. This is a *temporary* change, and the agent can choose either to wait for the guard to move or to detour around it.
2. **Collapsing routes (`route_blocked`).** At a scheduled step, the `C` tiles become walls. The tiles are always placed on the agent's shortest route, so the collapse invalidates the current plan and forces replanning. This is a *permanent* change. As a safety rule, a tile never collapses while the agent is standing on it; the collapse is delayed until the agent moves off.
3. **Constraint change (`rule_changed`).** At a scheduled step, the environment signals that the keypad's rules have changed. The CSP module and the agent's FSM handle this event: if the previously found code no longer satisfies the new rules, the door re-locks and the agent must return to the terminal.

Because these events change the world while the agent is moving, a fixed precomputed action sequence fails. The agent must observe the world and adapt.

## 4.3 Levels

| Level | Size | Dynamic elements | Purpose |
|---|---|---|---|
| 1 Easy | 11 × 15 | None | Static baseline for comparing search algorithms |
| 2 Medium | 14 × 20 | 1 guard patrolling the hall to the terminal; the shortest route to the key collapses at step 8 | Tests replanning and guard handling separately |
| 3 Hard | 19 × 20 | 2 guards (one in a single-width corridor); the obvious route collapses at step 6, leaving a longer detour; mud on the alternative route; puzzle rule change at step 70 | Combines all three types of change |

*(Insert screenshots of each level here, and Level 3 before and after the collapse.)*

## 4.4 Procedurally generated levels

To evaluate the agent beyond three hand-made maps, `random_level(seed)` generates new rooms. It places walls at random (about 22% density) and mud (about 8%), encloses the exit behind a single door, and places S, K and T at random. It then adds one guard on a horizontal run of floor cells, plus a collapsible tile on the shortest start-to-key route. Each candidate level is validated with breadth-first search, and is rejected and regenerated unless:

- every leg S → K → T → D → E is reachable;
- the exit is reachable *only* through the door;
- removing the guard's entire patrol route leaves the map connected, so the agent can never be permanently trapped;
- the map is still solvable after the collapse.

## 4.5 Reproducibility and validation

All randomness comes from a seeded generator (`random.Random(seed)`):

- **Seed 0** reproduces each level exactly as drawn.
- **Any other seed** randomises where each guard starts on its loop and which way it walks.

The same seed always produces the same run, which allows repeated trials (30 seeds per configuration) with reproducible results.

Maps are validated when they load. Missing or duplicate key cells, rows of unequal length, unknown symbols, and patrol routes that cross walls or skip cells all raise a descriptive `LevelError`. The module has 46 automated tests covering loading, costs, the door, each event type, the guard safety rules, reproducibility and generator guarantees.
