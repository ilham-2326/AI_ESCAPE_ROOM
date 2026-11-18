# Member 5 — Evaluation, Results and Reporting

## 1. Overview

Member 5 is responsible for evaluating the performance and reliability of the integrated AI Escape Room system.

The evaluation includes:

- Automated testing of Member 4's integrated AI agent.
- Comparison of BFS, Dijkstra, Greedy Best-First Search and A*.
- Repeated experiments across three predefined levels.
- Statistical analysis of performance metrics.
- Comparison with a non-replanning baseline agent.
- Generation of performance charts and experimental reports.
- Analysis of limitations and threats to validity.

## 2. Files

| File | Description |
|---|---|
| `evaluate.py` | Automated evaluation of the integrated agent |
| `baseline.py` | Plan-once baseline evaluation |
| `RESULTS_ANALYSIS.md` | Statistical analysis and algorithm comparisons |
| `BASELINE_COMPARISON.md` | Baseline methodology, results and findings |
| `results/raw_results.csv` | Individual adaptive-agent experiment results |
| `results/algorithm_summary.csv` | Mean and standard deviation by algorithm |
| `results/level_algorithm_summary.csv` | Performance statistics by level and algorithm |
| `results/bfs_astar_paired.csv` | Paired BFS and A* comparison |
| `results/seed44_results.csv` | Additional observations for seed 44 |
| `results/baseline_raw.csv` | Individual baseline experiment results |
| `results/baseline_summary.csv` | Baseline summary statistics |
| `results/run_metadata.json` | Adaptive evaluation configuration |
| `results/baseline_metadata.json` | Baseline evaluation configuration |
| `results/charts/` | Six performance and baseline comparison charts |

## 3. Evaluation Methodology

The integrated agent was evaluated in headless mode, without opening the Pygame GUI.

The experimental configuration included:

- **Levels:** Easy, Medium and Hard
- **Algorithms:** BFS, Dijkstra, Greedy and A*
- **Random seeds:** 1–30 and 44
- **Maximum simulation steps:** 3,000 per trial
- **Total adaptive-agent trials:** 372

Each algorithm was evaluated under the same level and seed combinations.

The following metrics were recorded:

- Success rate
- Completion time
- Simulation steps
- Path cost
- Nodes expanded
- Replanning operations
- Waiting actions

Mean and sample standard deviation were calculated to compare algorithm performance.

## 4. Search Algorithm Comparison

All four algorithms successfully completed their 93 recorded trials.

| Algorithm | Success Rate | Mean Path Cost | Mean Nodes Expanded |
|---|---:|---:|---:|
| BFS | 100% | 121.39 | 1690.91 |
| Dijkstra | 100% | 111.17 | 1388.53 |
| Greedy | 100% | 102.29 | 206.42 |
| A* | 100% | 95.43 | 547.86 |

A* achieved the lowest average path cost, while Greedy expanded the fewest nodes.

BFS explored the most nodes and had the highest average path cost in these experiments.

These findings describe the tested configurations and do not guarantee identical performance on other maps.

Detailed statistics, standard deviations and comparisons are available in `RESULTS_ANALYSIS.md`.

## 5. Baseline Comparison

The integrated adaptive agent was compared with a simpler plan-once baseline.

The adaptive agent can replan when obstacles block its route. The baseline plans a route for each navigation objective but does not replan while following that route.

Both agents use the same environment, search algorithms, FSM and CSP solver.

### Overall Results

| Agent | Successful Trials | Success Rate |
|---|---:|---:|
| Adaptive Agent | 372/372 | 100% |
| Plan-Once Baseline | 124/372 | 33.3% |

### Baseline Results by Level

| Level | Baseline Success Rate |
|---|---:|
| Easy | 100% |
| Medium | 0% |
| Hard | 0% |

The adaptive agent completed all recorded trials, while the baseline succeeded only on Level 1.

These results demonstrate the importance of adaptive replanning in the tested dynamic environments. However, the baseline intentionally uses a simpler navigation policy.

Further details are available in `BASELINE_COMPARISON.md`.

## 6. Performance Visualisation

Six charts were generated to illustrate the experimental findings.

**Search Algorithm Evaluation:**

- `mean_path_cost.png`
- `mean_nodes_expanded.png`
- `mean_replans.png`
- `mean_simulation_steps.png`

**Baseline Comparison:**

- `baseline_success_rates.png`
- `astar_success_by_level.png`

All charts are available in `results/charts/`.

## 7. How to Run

Open a terminal in the main project directory.

The evaluation requires the environment, search, CSP and integrated agent modules from the other team members.

Run the adaptive-agent evaluation:

```bash
python member_5/evaluate.py --seeds 1-30,44
```

Run the baseline comparison:

```bash
python member_5/baseline.py --seeds 1-30,44
```

Both evaluations run without opening the graphical interface.

The generated results are stored in `member_5/results/`.

## 8. Known Limitations and Threats to Validity

- Only three predefined levels were evaluated, limiting generalisation to other environments.
- Fixed random seeds improve reproducibility but do not cover every possible obstacle configuration.
- The random-level generator was not included in the integrated evaluation.
- The baseline is intentionally simpler and does not use an advanced recovery strategy.
- Completion time depends on the hardware and execution environment.
- The previously reported seed-44 failure was not reproduced in the recorded adaptive-agent trials.
- Additional generated-level and difficult dynamic-obstacle tests would strengthen the findings.

## 9. Individual Contribution

Member 5 prepared the automated evaluation workflow, collected experimental performance data, produced statistical summaries and visualisations, and developed the plan-once baseline comparison.

The evaluation work provides experimental evidence for comparing search algorithms, assessing the importance of replanning, and supporting the final group report and demonstration.
