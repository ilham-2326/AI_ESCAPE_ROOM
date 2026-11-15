# AI Escape Room

An intelligent agent that solves a dynamic escape room on its own. The agent explores
a grid world, picks up the key, solves the keypad puzzle at the terminal, unlocks the
door and reaches the exit. Along the way it has to deal with moving guards, collapsing
floor tiles and puzzle rules that change mid-game.

## Modules

| Folder | Member | What it does |
|---|---|---|
| `member_1/` | Environment & Dynamics | Grid maps, terrain costs, door, dynamic events, random level generator |
| `member_2/` | Search & Path Planning | BFS, UCS, A* and replanning when the route gets blocked |
| `member3_csp/` | CSP Puzzle Solver | Keypad code solver with backtracking, forward checking and rule updates |
| `member_4/` | Agent & Integration | Game controller (FSM) that connects all the modules |
| `member_5/` | Evaluation | Benchmarks and results |

## Requirements

Python 3.10+, plus `pytest` to run the tests and `matplotlib` to make the charts.

CSCI218 group project, University of Wollongong in Dubai.
