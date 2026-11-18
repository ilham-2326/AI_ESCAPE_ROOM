# Member 5 — Evaluation, Results and Reporting

## 1. Overview

Member 5 focuses on evaluating the integrated AI Escape Room system and analysing its performance.

The evaluation includes:

- Automated testing of the integrated AI agent.
- Comparison of four search algorithms.
- Experiments across three predefined levels.
- Repeated trials using fixed random seeds.
- Collection of performance metrics.
- Statistical analysis and visualisation of results.

## 2. Files

| File | Description |
|---|---|
| `evaluate.py` | Automated evaluation of the integrated agent |
| `results/raw_results.csv` | Experimental results from individual trials |
| `results/run_metadata.json` | Experiment configuration and metadata |
| `README.md` | Evaluation documentation |

## 3. Evaluation Methodology

The evaluation runs the integrated Member 4 agent without opening the Pygame interface.

Three predefined levels are tested using four search algorithms:

- Breadth-First Search (BFS)
- Dijkstra
- Greedy Best-First Search
- A*

Experiments use fixed random seeds to support reproducibility.

## 4. Performance Metrics

The evaluation records:

- **Success Rate** — Percentage of trials where the agent escapes.
- **Completion Time** — Time taken to execute a trial.
- **Path Cost** — Total movement cost.
- **States Explored** — Number of search nodes expanded.
- **Replans** — Number of route replanning operations.
- **Waits** — Number of waiting actions.

## 5. How to Run

Open a terminal in the main project directory.

Run the evaluation:

```bash
python member_5/evaluate.py
```

Run using seeds 1–30 and 44:

```bash
python member_5/evaluate.py --seeds 1-30,44
```

The experimental results are saved in the `member_5/results` folder.

## 6. Experimental Results

The evaluation results are stored in `raw_results.csv`.

The collected data will be used to calculate mean performance, standard deviation, success rates and comparisons between search algorithms.

## 7. Known Limitations

- Evaluation is based on three predefined levels.
- Performance may vary with different random seeds and dynamic events.
- Results depend on the current implementation of the integrated agent.
- Additional experiments are needed to evaluate performance on a wider variety of generated levels.

## 8. Individual Contribution

Member 5 developed the automated evaluation workflow, organised experimental results, and contributed to performance analysis, comparison of search algorithms, final report preparation and demonstration materials.
