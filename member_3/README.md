# Member 3: CSP solver integration

See START_HERE.md for run commands. Runtime: Python 3.10+, standard library only. Tests: `python3 -m unittest discover -v`. Demo: `python3 demo.py`.

## Public API

| Function/class | Contract |
|---|---|
| Puzzle(domains, total, greater, all_different, revision) | Four nonempty digit domains; default total=20, greater=(0,2), distinct digits, revision=1. Input containers are copied into immutable tuples. |
| generate_puzzle(seed, difficulty, revision) | Deterministic satisfiable instance; easy/medium/hard use domain sizes 4/7/10. No uniqueness guarantee. |
| solve(puzzle, method) | method='optimized' or 'baseline'; returns Result with solved/unsatisfiable, code or None, revision, method and Stats. Fresh search; no mutation or cache. |
| validate_code(puzzle, code) | Boolean validity of a four-character ASCII digit string against current domains and constraints. |
| change_rules(puzzle, total=..., greater=...) | New revision; omitted rules unchanged. May be unsatisfiable. |
| KeypadController(puzzle) | Adapter for one keypad with serial events. Solving and submission are separate. |

## Member 4: minimal integration

Place csp_solver.py and keypad.py alongside the main script, or adjust imports to the repo package layout.

```python
from keypad import KeypadController
from csp_solver import change_rules

keypad = KeypadController()  # initialize once per room

# On entering the FSM's SOLVE_PUZZLE state:
result = keypad.solve_current()
if result.status == 'solved':
    accepted = keypad.submit(result.code, result.revision)
    if accepted and keypad.can_unlock(has_key=True):
        pass  # transition to OPEN_DOOR using the actual inventory value
else:
    pass  # keep locked, show failure, use the game's recovery policy

# On a rule-change event, before any later submission/unlock action:
keypad.update_rules(change_rules(keypad.puzzle, total=21))
# Refresh displayed clues and transition back to SOLVE_PUZZLE.
```

Replace `has_key=True` with the game's real inventory flag. Never use this literal in the final game's unlock decision. Always call update_rules for a rule change, then require a fresh current submission. It rejects same/older revisions. The controller clears cached result and solved state on updates. Invalid submissions clear solved state. Do not bypass its lifecycle by assigning puzzle or solved attributes directly. Controller assumes one serialized event stream; it is not a thread-safe service.

The code may contain a leading zero and must remain a string. Any satisfying current code is accepted, not just the first one found. A clue change might produce no valid code; the game must display that state and follow an explicit recovery policy. Use the default total 20 -> 21 transition for the known solvable demonstration, or precheck proposed updates. If the door has already opened, the group's game design must define whether later changes relock it. The adapter checks permission to unlock and does not manipulate a physical/graphical door.

## Evaluation

`python3 benchmark.py --seeds 100 --repeats 5 --output results` runs the documented default configuration. experiment_config.json records the defaults as documentation; the CLI arguments control actual execution. Three domain sizes x three scenarios x 100 seeds x five repeats x two methods = 9,000 observations. Summary statistics use repeat-averaged per-instance values, then aggregate across seeds. The metadata records Python/platform, UTC time and experiment settings. Charting is optional and requires matplotlib; its version affects only plotting, not solver behavior.

Metrics: assignments_tried counts search attempts, not filtering probes; constraint_checks includes both. backtracks counts exhausted nonterminal search states. values_pruned includes removals in failed branches. recursive_calls includes root and terminal states. elapsed_ms measures solve only, including domain setup. Warm-up, generation, validation and CSV writing are excluded. solved_rate is the share of instances with a solution found, not a correctness rate on deliberately impossible puzzles. valid_result_rate uses checked returned solutions or failure statuses; failure agreement alone is not independent verification. Use the exhaustive oracle tests as additional evidence.

## Final integrated acceptance checks

- Agent reaches terminal, sees the correct domains and constraints, solves, obtains/has key, unlocks and reaches exit.
- Change rules before solving and immediately before unlock; old result cannot authorize opening.
- Impossible rules leave the door locked and game responsive.
- Multiple valid solutions and leading zeros work.
- Repeat on easy/medium/hard rooms and record actual room success and completion time.

The package has component and controller tests, not an included full Pygame environment. Official rubric alignment and report text are in REPORT_MEMBER3.md and VIVA_AND_REFLECTION.md. No grades or flawless behavior in unseen integration code are guaranteed.
