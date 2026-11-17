
# Member 4 — Agent Brain, Integration and GUI

## 1. Overview

Member 4 is responsible for integrating the AI Escape Room components into one working application.

The implementation includes:
- Finite State Machine (FSM) for agent decision-making.
- Integration with Member 1's environment.
- Integration with Member 2's search algorithms.
- Integration with Member 3's CSP keypad solver.
- Pygame graphical user interface (GUI).
- Live simulation statistics and controls.
- Automated integration testing.

## 2. Files

| File | Description |
|---|---|
| `agent.py` | FSM, agent decisions and component integration |
| `main.py` | Application entry point and simulation loop |
| `renderer.py` | Pygame interface and statistics display |
| `test_agent.py` | Automated integration tests |

## 3. Finite State Machine

The agent follows these states:

1. FIND_KEY — Navigate to the key and collect it.
2. GO_TO_TERMINAL — Navigate to the puzzle terminal.
3. SOLVE_PUZZLE — Solve the keypad using Member 3's CSP solver.
4. GO_TO_DOOR — Navigate to the locked door and unlock it when permitted.
5. GO_TO_EXIT — Navigate through the unlocked door toward the exit.
6. ESCAPED — The agent successfully reaches the exit.
7. FAILED — The agent cannot complete the required objective.

The FSM coordinates navigation, puzzle solving and unlocking.

## 4. Component Integration

### Member 1 — Environment

The environment provides the grid, walls, terrain costs, keys, terminals, doors, exits and dynamic events.

### Member 2 — Search Algorithms

The agent uses Member 2's search module to plan routes.

Supported algorithms:
- Breadth-First Search (BFS)
- Dijkstra
- Greedy Best-First Search
- A*

The agent can replan when a route becomes invalid.

### Member 3 — CSP Solver

The agent uses the CSP solver to solve keypad puzzles.

The keypad controller validates solutions and checks the key requirement before allowing the door to unlock.

### Member 4 — FSM and GUI

The FSM coordinates the complete escape sequence.

The Pygame interface displays the environment, agent position, route visualization, current FSM state and performance metrics.

## 5. GUI Controls

| Key | Action |
|---|---|
| Space | Pause / resume |
| R | Reset simulation |
| 1 | BFS |
| 2 | Dijkstra |
| 3 | Greedy |
| 4 | A* |
| Up / Down | Adjust simulation speed |
| Esc | Exit |

## 6. How to Run

Open a terminal in the project root directory.

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install Pygame:

```bash
python -m pip install pygame
```

Run a predefined level:

```bash
python member_4/main.py --level 1
```

Other levels:

```bash
python member_4/main.py --level 2
python member_4/main.py --level 3
```

Run a generated level:

```bash
python member_4/main.py --random 7
```

## 7. Automated Testing

Run the integration tests:

```bash
python member_4/test_agent.py
```

Observed result:

```text
Ran 6 tests in 0.018s

OK
```

The tests verify:
- Initial FSM state
- Key requirement for unlocking
- Agent reset
- Complete escape sequence
- Multiple generated levels
- All four search algorithms

## 8. Manual Testing Results

### Predefined Levels — A*

| Level | Result | Steps | Nodes Expanded | Replans | Waits | Travel Cost |
|---|---|---:|---:|---:|---:|---:|
| Easy | ESCAPED | 57 | 122 | 0 | 0 | 62 |
| Medium | ESCAPED | 81 | 325 | 7 | 0 | 80 |
| Hard | ESCAPED | 117 | 754 | 2 | 5 | 117 |

### Level 1 — Search Algorithm Comparison

| Algorithm | Result | Steps | Nodes Expanded | Replans | Travel Cost |
|---|---|---:|---:|---:|---:|
| BFS | ESCAPED | 53 | 300 | 2 | 64 |
| Dijkstra | ESCAPED | 57 | 438 | 4 | 62 |
| Greedy | ESCAPED | 57 | 130 | 1 | 68 |
| A* | ESCAPED | 57 | 122 | 0 | 62 |

All four algorithms successfully completed Level 1.

In these runs, A* and Dijkstra achieved the lowest observed travel cost. A* also expanded fewer nodes than the other algorithms in the comparison.

These observations are based on individual runs and are not general performance guarantees.

## 9. Known Limitations

- Search performance varies depending on the level layout and algorithm.
- The GUI demonstrates the agent's decisions but does not allow manual agent movement.
- Random levels and dynamic events may produce different execution statistics.
- Further targeted tests are needed for puzzle rule changes and difficult dynamic-obstacle scenarios.

## 10. Individual Contribution

Member 4 implemented the FSM-based agent controller, integrated the environment, search algorithms and CSP solver, developed the Pygame GUI and simulation controls, and performed manual and automated integration testing.

The final application demonstrates an autonomous agent that collects a key, solves a keypad puzzle, unlocks a door and reaches the exit.
