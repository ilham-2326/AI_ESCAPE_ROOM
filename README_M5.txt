MEMBER 5 - TASK 1: HEADLESS EVALUATION

What this adds:
- evaluate.py: runs the integrated Member 4 agent without opening Pygame.
- results/raw_results.csv: raw measurements from the completed evaluation run.
- results/run_metadata.json: seeds, levels, algorithms and run configuration.

Evaluation configuration used for the supplied CSV:
- Levels: 1, 2, 3
- Algorithms: bfs, dijkstra, greedy, astar
- Seeds: 1 through 30, plus seed 44
- Maximum simulation steps per trial: 3000
- Total trials: 372

Run from the project root:
    python member_5/evaluate.py

To reproduce the exact supplied seed set explicitly:
    python member_5/evaluate.py --seeds 1-30,44 --max-steps 3000

Dependencies: Python standard library plus the project's own modules. This
headless evaluator does not import or launch Pygame.

CSV measurement definitions:
- completion_time_seconds: wall-clock time for one complete headless trial
- simulation_steps: number of agent update ticks
- path_cost: accumulated movement cost recorded by the agent
- states_explored: cumulative nodes_expanded recorded by the agent's planner
- replans: replan counter recorded by the agent
- waits: wait counter recorded by the agent
- success: true only if the FSM reaches ESCAPED

Important:
The CSV is raw trial data, not yet the mean/standard-deviation summary or
baseline comparison. Those are subsequent Member 5 tasks. Seed 44 was included
explicitly; all 12 combinations for seed 44 (3 levels x 4 algorithms) escaped
in this run. Do not describe seed 44 as a failure based on this run.
