"""Paired repeated trials, correctness checks and reproducible experiment metadata."""
import argparse
import csv
import json
import platform
import statistics
from pathlib import Path
from dataclasses import asdict
from datetime import datetime, timezone
from csp_solver import generate_puzzle, solve, change_rules, validate_code

METRICS = ('elapsed_ms', 'assignments_tried', 'backtracks', 'constraint_checks',
           'values_pruned', 'recursive_calls')

def run(output='results', seeds=100, repeats=5):
    if seeds < 1 or repeats < 2:
        raise ValueError('At least one seed and two repeats required')
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for difficulty in ('easy', 'medium', 'hard'):
        for seed in range(seeds):
            base = generate_puzzle(seed, difficulty)
            # Reversing a strict inequality necessarily invalidates any old solution.
            changed = change_rules(base, greater=base.greater[::-1])
            impossible = change_rules(base, total=100)
            cases = [('original', base), ('rule_changed', changed), ('impossible', impossible)]
            for scenario, puzzle in cases:
                # Warm up both implementations outside measured observations.
                for method in ('baseline', 'optimized'):
                    solve(puzzle, method)
                for repeat in range(repeats):
                    paired = []
                    methods = ('baseline', 'optimized') if (seed + repeat) % 2 == 0 else ('optimized', 'baseline')
                    for method in methods:
                        r = solve(puzzle, method)
                        valid = r.status == 'unsatisfiable' if r.code is None else validate_code(puzzle, r.code)
                        if not valid or (scenario == 'original' and r.code is None) or (scenario == 'impossible' and r.code is not None):
                            raise AssertionError('Invalid experiment result')
                        paired.append(r.status)
                        rows.append(dict(difficulty=difficulty, seed=seed, scenario=scenario,
                            repeat=repeat, revision=r.revision, method=method, status=r.status,
                            valid=int(valid), **asdict(r.stats)))
                    if len(set(paired)) != 1:
                        raise AssertionError('Solvers disagree about satisfiability')
    def write(name, data):
        with (out / name).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)
    write('raw_metrics.csv', rows)
    summary = []
    for difficulty in ('easy', 'medium', 'hard'):
        for scenario in ('original', 'rule_changed', 'impossible'):
            for method in ('baseline', 'optimized'):
                group = [r for r in rows if (r['difficulty'],r['scenario'],r['method']) == (difficulty,scenario,method)]
                row = dict(difficulty=difficulty,scenario=scenario,method=method,
                    instances=seeds, repeats=repeats, observations=len(group),
                    valid_result_rate=sum(r['valid'] for r in group)/len(group),
                    solved_rate=sum(r['status']=='solved' for r in group)/len(group))
                for metric in METRICS:
                    # Average timing repetitions for each instance before aggregation;
                    # this avoids treating repeats as independent puzzle instances.
                    values = [statistics.mean(r[metric] for r in group if r['seed']==s) for s in range(seeds)]
                    row[metric+'_mean'] = statistics.mean(values)
                    row[metric+'_std'] = statistics.stdev(values) if len(values)>1 else 0.0
                    row[metric+'_median'] = statistics.median(values)
                summary.append(row)
    write('summary.csv', summary)
    metadata = dict(utc=datetime.now(timezone.utc).isoformat(), python=platform.python_version(),
        platform=platform.platform(), seeds=seeds,repeats=repeats, observations=len(rows),
        timing='perf_counter; one warm-up per method/case; alternating execution order',
        aggregation='per-instance repeat means, then mean/sample SD/median across seeds',
        note='Valid-result rate includes agreement-based unsatisfiable results; generated original cases are guaranteed satisfiable. Changed-case satisfiability agreement is not an independent proof.')
    (out/'metadata.json').write_text(json.dumps(metadata,indent=2))
    print(f'Wrote {len(rows)} observations and {len(summary)} summaries to {out}')
    return summary

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', default='results')
    parser.add_argument('--seeds',type=int,default=100)
    parser.add_argument('--repeats',type=int,default=5)
    args=parser.parse_args()
    run(args.output,args.seeds,args.repeats)
