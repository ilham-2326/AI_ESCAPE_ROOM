# Member 5 — Task 2: Results analysis

Source: `member_5/results/raw_results.csv` from the Task 1 package. Results are descriptive statistics of recorded trials; no new experiments were run for this analysis.

## Experimental design

Three hand-made levels, four search algorithms, and 31 fixed seeds (1–30 and 44): 372 trials. All 372 rows record `success=True`, so observed success rate is 100% for each algorithm. This does not establish universal reliability.

## Overall algorithm comparison

| Algorithm | Trials | Success | Mean cost ± SD | Mean nodes ± SD | Mean steps ± SD | Mean replans ± SD |
|---|---:|---:|---:|---:|---:|---:|
| BFS | 93 | 100% | 121.39 ± 60.18 | 1690.91 ± 1526.04 | 118.60 ± 62.57 | 3.04 ± 2.45 |
| Dijkstra | 93 | 100% | 111.17 ± 52.45 | 1388.53 ± 1230.14 | 111.59 ± 55.56 | 2.70 ± 2.27 |
| Greedy | 93 | 100% | 102.29 ± 28.92 | 206.42 ± 170.69 | 95.73 ± 32.58 | 1.30 ± 1.36 |
| A* | 93 | 100% | 95.43 ± 29.33 | 547.86 ± 375.85 | 95.06 ± 32.32 | 2.14 ± 2.03 |

Standard deviations are sample standard deviations (n−1). Metrics are averaged over successful trials; all recorded trials succeeded. Wall-clock times are machine-dependent and should not be treated as portable algorithm benchmarks.

## BFS versus A*

The `bfs_astar_paired.csv` file compares BFS and A* for each identical level/seed combination, avoiding a mismatch in trial conditions. Compare path cost and nodes expanded together; search efficiency and travel-cost efficiency are not the same.

## Seed 44

All 12 seed-44 records (3 levels × 4 algorithms) report success. Therefore the supplied dataset does not reproduce the previously mentioned seed-44 failure; it should not be presented as an observed failure. The separate `seed44_results.csv` contains the actual observations.

## Threats to validity

The following factors limit how broadly the recorded results can be interpreted:

1. **Limited level variety (external validity).** The experiments cover only three hand-made levels. Their layouts, terrain costs, and obstacle arrangements may not represent other escape-room maps. The observed ranking of algorithms may change on different layouts or larger maps.
2. **Fixed seeds and event coverage (external validity).** Fixed seeds make the trials reproducible, but 31 selected seeds cannot cover every possible dynamic event or obstacle configuration. In addition, changing a seed does not necessarily change every predefined level or metric; the effective variation introduced by the environment needs to be checked. The random-level generator was not evaluated in this dataset, so the results cannot be generalised to generated maps.
3. **No independent non-replanning baseline (comparative validity).** All reported trials evaluate the integrated agent with the selected search algorithms. A separate agent that plans once and does not replan was not tested. Consequently, these results do not establish how much replanning improves success or efficiency. A fair baseline must use the same levels, seeds, stopping rules, and metrics.
4. **Timing and metric interpretation (measurement validity).** Wall-clock completion times depend on the computer, Python runtime, and background load, and are not directly comparable across machines. Nodes expanded measure search effort, while path cost measures movement cost; neither alone captures overall agent quality. Means across all three levels can also hide level-specific differences, so per-level results should be consulted.
5. **Failure-case coverage (internal validity).** All 372 recorded trials report success, including all 12 trials with seed 44. The previously reported seed-44 failure was **not reproduced** under this configuration. This does not rule out failures under other initial conditions, event schedules, or generated levels. Targeted failure tests are needed before claiming broad reliability.

## Limitations and next work

Implement and run the non-replanning baseline under the same conditions; inspect how seeds affect dynamic events; and test additional generated levels and difficult obstacle scenarios. Report the baseline results and any observed failures separately rather than inferring them from the current successful trials.
