# Member 5 — Task 3: Baseline Comparison

## 1. Overview
This experiment compares Member 4's adaptive AI agent against a deliberately simpler **plan-once-per-objective** baseline using the same environment, algorithms, seeds, and maximum simulation steps.

## 2. Baseline Definition
The baseline computes a route at the beginning of each navigation objective (key, terminal, door, exit) and **never replans while following that objective**. If a moving obstacle blocks the next tile, it waits on the original route. If a collapsed tile makes the route permanently invalid, it fails. Planning a new route after reaching a new objective is permitted; the escape room has multiple sequential goals, so a single route from start to exit is not sufficient. The baseline still uses the same FSM and CSP keypad solver as the adaptive agent.

The adaptive agent uses Member 4's original code and can replan in response to obstacles or invalid routes. This baseline is intentionally less robust, not a fully independent alternative AI implementation.

## 3. Experimental Setup
- 3 predefined levels × 4 algorithms (BFS, Dijkstra, Greedy, A*) × 31 seeds (1–30 and 44) × 2 agent types = **744 trials**.
- Maximum 3,000 simulation steps per trial.
- Headless execution; identical map, seed, algorithm and objective sequence for each paired comparison.
- Metrics: success, final state, runtime, simulation steps, path cost, nodes explored, replans, and waits.

## 4. Results

| Algorithm | Adaptive successes | Plan-once successes | Adaptive rate | Plan-once rate |
|---|---:|---:|---:|---:|
| BFS | 93/93 | 31/93 | 100% | 33.3% |
| Dijkstra | 93/93 | 31/93 | 100% | 33.3% |
| Greedy | 93/93 | 31/93 | 100% | 33.3% |
| A* | 93/93 | 31/93 | 100% | 33.3% |
| **Total** | **372/372** | **124/372** | **100%** | **33.3%** |

**Level-level findings:** The baseline escaped in every Level 1 trial (124/124), failed in every Level 2 trial (124/124), and timed out in every Level 3 trial (124/124). The adaptive agent escaped in all 372 trials.

The baseline's mean path cost, steps, and nodes expanded are **only calculated over successful runs** in `baseline_summary.csv`. Because baseline success occurs only on Level 1, its lower average path cost **must not** be interpreted as superior efficiency on the full benchmark. Failed runs are included in the success-rate denominator and preserved in the raw CSV.

The summary CSV includes mean and sample standard deviation for each numeric metric on successful runs. These are descriptive statistics; repeated seeds on the same hand-designed map are not independent samples of different maps.

## 5. Interpretation
The experiment provides evidence that adaptive replanning matters in this implementation, especially when routes become invalid or obstacles obstruct progress. However, the baseline policy is intentionally simple and does not attempt a sophisticated recovery strategy. The 66.7 percentage-point overall success-rate difference reflects this particular comparison, not a universal advantage across all environments.

## 6. Threats to Validity
1. **Only three predefined maps:** Results may not generalise to larger or differently structured escape rooms.
2. **Seed variation is limited:** Seeds vary obstacle dynamics but do not create 31 independently designed map layouts.
3. **Baseline design:** The plan-once agent fails on permanently blocked routes and can wait indefinitely behind an obstacle. A stronger baseline with bounded waiting or other recovery could perform better.
4. **Timeout threshold:** Level 3 baseline outcomes are classified as timeouts at 3,000 steps. Different thresholds could change the classification, although they do not demonstrate escape in the observed runs.
5. **Shared code:** Both agents reuse the same FSM, puzzle solver and search algorithms. The comparison isolates navigation policy more than overall AI architecture.
6. **Runtime measurement:** Wall-clock times can vary with hardware and background processes; simulation steps and success are more stable.
7. **Seed 44:** It is included in the fixed seed set, but these runs do not independently reproduce a special failure of the adaptive agent. Claims about a previously reported failure need a matching scenario and configuration.

## 7. Reproducibility
From the project root, with all member modules installed:

```bash
python member_5/baseline.py --seeds 1-30,44
```

Output files: `results/baseline_raw.csv`, `results/baseline_summary.csv`, `results/baseline_metadata.json`. Charts are provided separately under `results/charts/`.

## 8. Individual Contribution
Member 5's Task 3 work covers implementing and testing the comparison protocol, collecting paired results, summarising performance, and documenting interpretation and limitations. The final individual reflection should describe only work the student personally completed and can explain.
