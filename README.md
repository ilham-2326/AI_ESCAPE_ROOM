# AI Escape Room

**An intelligent agent for dynamic puzzle solving** · CSCI218 Group Project · University of Wollongong in Dubai

An autonomous agent escapes a grid-world escape room on its own. It has to:

1. navigate from the start to the **key** (`K`),
2. reach the **puzzle terminal** (`T`) and solve a keypad code puzzle,
3. unlock the **door** (`D`), which stays blocked until the puzzle is solved, and
4. reach the **exit** (`E`).

The room keeps changing while the agent moves. Guards patrol corridors, floor tiles collapse into walls, and the puzzle rules change partway through the game. The agent has to notice these changes and adapt: replan its route, wait for a guard to pass, or re-solve the puzzle.

---

## AI techniques used

| Problem | Technique |
|---|---|
| Finding a route through the grid | BFS, Dijkstra (uniform-cost search), Greedy best-first, A* with a Manhattan-distance heuristic |
| Routes blocked by events | Path validity checks and replanning from the agent's current position |
| Moving guards | A "wait-or-detour" strategy plus an extra cost for cells next to a guard |
| Keypad code puzzle | Constraint satisfaction problem (CSP): backtracking + MRV + forward checking |
| Puzzle rules changing | Versioned puzzle revisions, so an old solution can never unlock the door |
| Overall agent behaviour | Finite-state machine controller (Member 4) |

---

## Project structure

```
AI_ESCAPE_ROOM/
├── member_1/      Environment & Dynamics
├── member_2/      Search & Path Planning
├── member3_csp/   CSP Puzzle Solver
├── member_4/      Agent Controller & Integration
└── member_5/      Evaluation & Report
```

Each folder has its own README with full run commands and its API.

### Member 1: Environment & Dynamics (`member_1/`)

Builds the escape room world.

- Grid maps loaded from `.txt` files. Map symbols: `#` wall, `.` floor (cost 1), `~` mud (cost 3), `C` collapsible floor, `M` guard start, plus `S K T D E`.
- Three hand-designed levels of increasing difficulty:

  | Level | Size | Dynamics |
  |---|---|---|
  | 1 Easy | 11×15 | None (baseline) |
  | 2 Medium | 14×20 | 1 patrolling guard; the short route to the key collapses at step 8 |
  | 3 Hard | 19×20 | 2 guards, a collapse at step 6, mud on the detour, puzzle rules change at step 70 |

- A random level generator (`random_level(seed)`) that only produces solvable rooms, for large experiments.
- Each step the environment emits events (`obstacle_moved`, `route_blocked`, `rule_changed`) for the other modules to react to.
- 46 automated tests.

### Member 2: Search & Path Planning (`member_2/`)

Moves the agent through the room.

- Four algorithms: **BFS**, **Dijkstra**, **Greedy best-first** and **A\***.
- A* uses Manhattan distance. With 4-directional moves and a minimum step cost of 1, this heuristic is admissible and consistent, so A* always finds the cheapest path.
- `navigate()` runs a plan step by step and replans from the agent's current position whenever the remaining path gets blocked.
- Two strategies for moving guards: **replan** and **wait-or-detour**.
- A 960-run benchmark with CSV results and charts in `member_2/results/`.
- 69 automated tests.

### Member 3: CSP Puzzle Solver (`member3_csp/`)

Solves the 4-digit keypad code at the terminal.

- **Variables:** the four code digits. **Domains:** allowed digits 0–9.
- **Constraints:** the digits add up to a target total (default 20), one digit is greater than another (default: first > third), and all digits are different.
- **Optimised solver:** backtracking with MRV (minimum remaining values) and forward checking. It is compared against a plain backtracking baseline.
- `change_rules()` creates a new puzzle revision when the rules change. `KeypadController` rejects answers from older revisions, and unsolvable rule sets keep the door locked.
- Easy, medium and hard puzzles have domain sizes of 4, 7 and 10.
- A 9,000-observation benchmark in `member3_csp/results/`.

### Member 4: Agent Controller & Integration (`member_4/`)

*(To be completed by Member 4.)* A finite-state machine connects the modules. It moves to the key, then the terminal, solves the puzzle, opens the door and heads for the exit. It handles events in between, such as replanning on `route_blocked` and re-solving on `rule_changed`.

### Member 5: Evaluation & Report (`member_5/`)

*(To be completed by Member 5.)* End-to-end experiments across all levels: success rate, steps taken, completion time and replanning count.

---

## Key results so far

**Search (level 3, hard, average over 30 runs):**

| Algorithm + strategy | Success | Nodes expanded | Cost vs. optimal |
|---|---|---|---|
| BFS + replan | 100% | 3,572 | 2.66× |
| Dijkstra + replan | 100% | 3,147 | 1.95× |
| Greedy + replan | 90% | 1,694 | 2.41× |
| **A\* + wait-or-detour** | **100%** | **836** | **1.45×** |

A* with wait-or-detour expanded about 4× fewer nodes than BFS and took the cheapest routes.

**CSP (average assignments tried per puzzle):**

| Difficulty | Baseline backtracking | Backtracking + MRV + forward checking |
|---|---|---|
| Easy | 25.6 | 6.1 |
| Medium | 67.6 | 6.1 |
| Hard | 143.4 | 6.4 |

The optimised solver's effort stays almost flat as puzzles get harder, while the baseline's effort grows quickly.

---

## Getting started

**Requirements:** Python 3.10+. Everything runs on the standard library. `pytest` is needed for the tests, and `matplotlib` only for the charts.

```bash
git clone https://github.com/ilham-2326/AI_ESCAPE_ROOM.git
cd AI_ESCAPE_ROOM
pip install pytest matplotlib
```

**Run the demos:**

```bash
cd member_1 && python demo_environment.py --play 3      # watch level 3's guards and collapse
cd member_2 && python demo_search.py --watch 3          # watch A* escape level 3 live
cd member3_csp && python demo.py                        # solve, change the rules, re-solve
```

**Run the tests:**

```bash
pytest member_1/tests          # 46 tests
pytest member_2/tests          # 69 tests
cd member3_csp && python -m unittest discover -v
```

---

## Team

| Member | Role |
|---|---|
| Ilham Shaikh | Environment & Dynamics |
| Anasha Khan  | Search & Path Planning |
| Amir Hussain Khan    | CSP Puzzle Solver |
| Ahmed Nouman | Agent Controller & Integration |
| Zaid Rehman  | Evaluation & Report |


