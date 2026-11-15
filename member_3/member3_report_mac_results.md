# Member 3 — CSP puzzle solving##

These sections are written so that they can be included in the group's report. Number them to correlate with the common document. Data below was obtained using summary.csv that was submitted after the student ran the benchmark on their Mac using Python 3.12.7. These measurements are taken of the individual components, not of the final integrated game. Do not upload the metadata.json and raw_metrics.csv files, which were created by the Mac, as part of the submission; they are not included in this review.

## Motivation and measurable goals

The keypad does not have to be memorised and is a place where simultaneous restrictions need to be considered. This is directly expressed in a constraint satisfaction problem (CSP) as variables, domains and constraints. The goals are to generate a correct code if there is one, and report otherwise for configurations that are not satisfiable; invalidate stale results after changes; and compare performance of a search-and-filtering solver to a fixed-order backtracking solver on the same instances. Success is not based on a hidden generator answer, but on constraints validity and safe door behavior.

## Technical requirements and constructs

The implementation is based on Python 3.10+ and the standard library. Puzzle stores immutable domains, a target sum, an ordered inequality pair, a distinctness flag and a positive revision. Result records status, optional code, revision, method and metrics. KeypadController offers serial event handling, result invalidation and a key-dependent unlock condition. Display, grid movement and FSM scheduling are owned by the game integration component. 
For X={X0,X1,X2,X3}, each Xi belongs to Di, where Di is a nonempty subset of {0,...,9}. AllDifferent(X), X0>X2 and sum(Xi)=20 are the default constraints. Codes are 4 letter strings, including leading zeros. The indices in code start at 0. If distinctness is on, an assigned digit is duplicated in a partial assignment A, or if both endpoints are assigned, the partial assignment A is rejected if the inequality is not satisfied, or if the partial assignment A cannot be completed under domain bounds. With U the unassigned positions, the bounds are:
sum(A) + sum(min(Di), i in U) <= target <= sum(A) + sum(max(Di), i in U).
If a complete assignment, these bounds become equalities. They are required but not sufficient for sum-constraint propagation.

## Algorithm and design justification

Backtracking is done in a step-wise fashion to assign positions. MRV chooses an unassigned position with minimum remaining domain, and chooses the index of the position in case of a tie. It is based on the fail-first concept of choosing the most constrained variable from the University of California, Berkeley (n.d.a). Following each consistent assignment, incompatible values are pruned from each of the remaining domains (University of California, Berkeley, n.d.b). These candidate checks are also performed by applying sum bounds to the implementation. Filtering does a single pass instead of propagation to a fixed point.

```text
SEARCH(assignment, domains):
    if all positions assigned: return code
    choose variable (MRV for optimized; index order for baseline)
    for value in ascending domain order:
        count attempted assignment
        if assignment plus value is inconsistent: continue
        copy domain mapping
        if optimized:
            filter every other unassigned domain against tentative assignment
            if any domain becomes empty: continue
        recursively search the extended assignment and copied domains
        if a solution is returned: return it
    count exhausted search state
    return failure
```

Domains are automatically restored in the parent domain when recursion returns from the branch-local copies. The same constraint checks and ascending values are used with both methods. The baseline is exactly the same, but no MRV is attached, and no forward pruning is done, but it does have normal partial consistency checks. This comparison is based on the combined MRV/filtering design, and does not take into account the individual effect of each feature. MRV-only and filtering-only ablations are potential future research. A returned complete assignment is sound since it meets all set constraints. This finite model has been completely searched: all unpruned values are eventually attempted and pruning never rejects a partial assignment that is not leading to a solution. This argument is supplemented by the independent oracle tests.
Before per-node consistency and filtering overhead, the worst case growth of search trees is O(d^n). Here n=4 and d<=10. A generalised implementation would require dealing with O(n²d) candidate-check work per node for this simple design of filtering and domain copies on the stack of recursion. The implementation is deliberately set to lock four keypad positions in and not general large scale CSP efficiency. Does not support AC-3, global AllDifferent propagation or incremental repair. Other families of networks are considered by Mackworth (1977) under the self-consistent network.

## Dynamic rules and integration

The rules and integration are dynamic. A rule update brings about a strictly newer change, and resets the old result and solved flag. The controller is expecting a current revision when the submission is made and checks the code against the current puzzle on submission. Solving is not enough to open a door, it is necessary to accept and have the key. An unsolvable puzzle becomes unsatisfiable and the door remains shut. The deterministic demo updates the default target from 20 to 21 and checks for old-code rejection, successful re-solving and key enforcement. It then changes the target to 100 and checks for safe failure. This sequence is for testing the adapter, and not the final Pygame game. The main loop should not call solving for each frame displayed, but rather when the puzzle-solving state is entered or when a rule-change event is received. Events have to be passed serially. Additional stale-result checks and synchronization is required for threaded integration.

## Experiments and results

The experiment is repeated 5 times with each of the 3 sizes of domains (4, 7, and 10), two approaches (original, reversed inequality, and impossible sum), and 100 seeds in each group – 9000 observations. Original puzzles are guaranteed satisfiable by construction. If you change the strict inequality in the original instance to become a weak inequality, you make all of the original satisfying assignments "unsatisfying" but you may also make the new instance unsatisfiable. The impossible sum is 100, above the maximum sum of four digits. The puzzle is the same for both methods.The same unchanging puzzle is given to both methods. Each case/method is warmed up, execution order alternates and timing excludes generation and CSV writing. Average is computed within each seed and then the mean, the sample standard deviation and the median calculated across 100 seeds, with repeated observations averaged within each seed. The results/summary.csv file has all the summary statistics, the raw_metrics.csv file has the replication data, and the metadata.json file has the execution environment. The summary CSV file is shown below and generated from the measured data. Time is measured in milliseconds, ± is the sample standard deviation of per-instance repeat means. These are not room completion times but component timings.

| Domain size | Method | Runtime mean ± SD (ms) | Assignments mean ± SD |
|---|---|---|---|
| 4 | baseline | 0.0279 ± 0.0213 | 25.57 ± 20.95 |
| 4 | optimized | 0.0947 ± 0.3951 | 6.11 ± 2.74 |
| 7 | baseline | 0.0644 ± 0.1111 | 67.63 ± 107.18 |
| 7 | optimized | 0.0722 ± 0.0322 | 6.11 ± 2.57 |
| 10 | baseline | 0.0856 ± 0.1488 | 143.36 ± 282.85 |
| 10 | optimized | 0.0812 ± 0.0292 | 6.43 ± 2.69 |

The summary uploaded shows that both methods solved all the original instances generated in each of the 18 groups for a valid-result rate of 1.0 across all groups. The individual Mac-generated observations have not been independently reviewed in this benchmark as the benchmark checks paired agreement before producing its summary. For easy 88/100 and medium and hard 100/100 puzzles, there was a reversed-inequality. All targets which were impossible were rejected. These ratios are only for this generator of instances and not a guarantee of success in general. If there is agreement on failure, it is not an independent proof; there are independent exhaustive oracle tests for additional correctness evidence on random small cases. This optimized method greatly reduced the number of attempted assignments. The means for the optimized method on the original cases were slightly lower (0.0812 vs 0.0856 ms) on the full domain cases, but lower means were found on the smaller domains for baseline. There was substantial variation in per-instance repeat means with the optimized easy_case runtime having a standard deviation of 0.3951ms and a mean of 0.0947ms. The summary does not give an idea about the observations that are causing the spread nor does it provide an indication of whether instance variation or system scheduling or other factors are predominant. These measurements are not statistically significant in terms of runtime improvement. Check raw measurement data before making more definitive statements. Assignments also are not included in probes, but in constraint_checks, therefore assignment does not imply computational speed. After the first assignment of candidates, sum bounds can be used to set impossible targets, which lead to few differences between methods. These are correctly rejected by both algorithms.

## Threats to validity

Four variable instances are very small, timings are sensitive to scheduling noise, and generator labels refer to the size of the domain and not the difficulty of the problem. The instance distribution is biased by a witness. First-solution search is not necessarily unique, and is value-ordering dependent. Rule-change measures only solving time for fresh solving, does not include event delivery, GUI rendering and door updates. The component benchmark was conducted on the student's Mac and final-game measurements are not guaranteed. Future evaluation should feature diverse constraint families, more powerful unsatisfiable examples, and ablations and end-to-end room success and latency.

## Implementation validation and evidence

Overall we have 10 test methods passed, six from the solver groups and four from the controller groups. Tested 300 generated instances with two methods, 200 small domain instances randomly generated with an independent exhaustive oracle checked with both methods, leading zeros, invalid input, immutable input snapshots, stale revisions, invalid submissions and key requirements, and tested cases that are known to be satisfiable or not. These are screenshots of the Mac, which show that the demo has been completed, and all ten tests passed (all 10 tests in 0.058 seconds). Earlier development environment outputs (test_results.txt, demo_output.txt) in the package are not to be used to display as Mac logs. The oracle enumerates the tuples that may satisfy the predicate, and verifies mathematical constraints without invoking the solver's predicate.

## Limitations and conclusion

This component can generate puzzles in a repeatable manner, solve the finites and also offers revision-aware validation for 4-digit keypads. It safely can handle several valid codes and impossible configurations. Uniqueness, full arc consistency and GUI animation/generalized puzzle sizes are outside of scope. The experiment allows for fewer search assignments and benefits in runtime are largely influenced by instance size and filtering overhead. The integrated application is responsible for the last end-to-end verification.

## References

Mackworth, A.K. (1977) ‘Consistency in networks of relations’, Artificial Intelligence, 8(1), pp. 99–118. Available at: https://www.cs.ubc.ca/~mack/Publications/AI77.pdf (Accessed: 14 November 2026).

University of California, Berkeley (n.d.a) ‘2.4 Ordering’, CS 188: Introduction to Artificial Intelligence. Available at: https://inst.eecs.berkeley.edu/~cs188/textbook/csp/ordering.html (Accessed: 14 November 2026).

University of California, Berkeley (n.d.b) ‘2.3 Filtering’, CS 188: Introduction to Artificial Intelligence. Available at: https://inst.eecs.berkeley.edu/~cs188/textbook/csp/filtering.html (Accessed: 14 November 2026).