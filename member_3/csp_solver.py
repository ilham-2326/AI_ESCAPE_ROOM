"""Member 3: pure-Python keypad CSP. No GUI or third-party dependencies."""
from dataclasses import dataclass, asdict
from random import Random
from time import perf_counter

@dataclass(frozen=True)
class Puzzle:
    domains: tuple = (tuple(range(10)),) * 4
    total: int = 20
    greater: tuple = (0, 2)  # zero-based: first digit > third digit
    all_different: bool = True
    revision: int = 1

    def __post_init__(self):
        # Detach mutable caller-owned containers so frozen puzzles stay immutable.
        object.__setattr__(self, "domains", tuple(tuple(d) for d in self.domains))
        object.__setattr__(self, "greater", tuple(self.greater))
        if type(self.all_different) is not bool:
            raise ValueError("all_different must be a boolean")
        if len(self.domains) != 4 or any(not d for d in self.domains):
            raise ValueError('Provide four nonempty digit domains')
        if any(type(v) is not int or not 0 <= v <= 9 for d in self.domains for v in d):
            raise ValueError('Domains must contain integers from 0 to 9')
        if any(len(set(d)) != len(d) for d in self.domains):
            raise ValueError('Duplicate domain values')
        if len(self.greater) != 2 or any(type(i) is not int or not 0 <= i < 4 for i in self.greater) or self.greater[0] == self.greater[1]:
            raise ValueError('greater must contain two distinct indices from 0 to 3')
        if type(self.total) is not int or type(self.revision) is not int or self.revision < 1:
            raise ValueError('Integer total and positive integer revision required')

@dataclass
class Stats:
    assignments_tried: int = 0
    backtracks: int = 0
    constraint_checks: int = 0
    values_pruned: int = 0
    recursive_calls: int = 0
    elapsed_ms: float = 0.0

@dataclass
class Result:
    status: str
    code: str | None
    revision: int
    method: str
    stats: Stats

    def to_dict(self):
        return asdict(self)


def _consistent(p, a, domains):
    if p.all_different and len(set(a.values())) != len(a):
        return False
    i, j = p.greater
    if i in a and j in a and a[i] <= a[j]:
        return False
    remaining = [k for k in range(4) if k not in a]
    partial = sum(a.values())
    return (partial + sum(min(domains[k]) for k in remaining) <= p.total <=
            partial + sum(max(domains[k]) for k in remaining))


def validate_code(puzzle, code):
    """Accept any satisfying four-digit string, including leading zero."""
    if not isinstance(code, str) or len(code) != 4 or any(c not in '0123456789' for c in code):
        return False
    a = dict(enumerate(map(int, code)))
    return all(a[k] in puzzle.domains[k] for k in a) and _consistent(puzzle, a, puzzle.domains)


def solve(puzzle, method='optimized'):
    """Fresh search per call. optimized = backtracking + MRV + forward checking.

    baseline = fixed variable order, same ascending value order, no pruning.
    Neither method mutates the puzzle or shares a previous solution.
    """
    if method not in ('optimized', 'baseline'):
        raise ValueError('method must be optimized or baseline')
    s = Stats()
    start = perf_counter()
    initial = {k: tuple(sorted(d)) for k, d in enumerate(puzzle.domains)}

    def check(a, ds):
        s.constraint_checks += 1
        return _consistent(puzzle, a, ds)

    def visit(a, ds):
        s.recursive_calls += 1
        if len(a) == 4:
            return ''.join(str(a[k]) for k in range(4))
        unassigned = [k for k in range(4) if k not in a]
        var = min(unassigned, key=lambda k: (len(ds[k]), k)) if method == 'optimized' else unassigned[0]
        for value in ds[var]:
            s.assignments_tried += 1
            trial = {**a, var: value}
            if not check(trial, ds):
                continue
            next_ds = ds.copy()
            possible = True
            if method == 'optimized':
                for k in unassigned:
                    if k == var:
                        continue
                    kept = tuple(v for v in ds[k] if check({**trial, k: v}, ds))
                    s.values_pruned += len(ds[k]) - len(kept)
                    if not kept:
                        possible = False
                        break
                    next_ds[k] = kept
            if possible:
                answer = visit(trial, next_ds)
                if answer is not None:
                    return answer
        s.backtracks += 1
        return None

    answer = visit({}, initial)
    s.elapsed_ms = (perf_counter() - start) * 1000
    return Result('solved' if answer is not None else 'unsatisfiable', answer,
                  puzzle.revision, method, s)


def generate_puzzle(seed=0, difficulty='medium', revision=1):
    """Generate satisfiable puzzles with a private witness; uniqueness not promised.

    Difficulty controls domain size, not guaranteed measured search difficulty.
    """
    sizes = {'easy': 4, 'medium': 7, 'hard': 10}
    if difficulty not in sizes:
        raise ValueError('difficulty must be easy, medium or hard')
    rng = Random(seed)
    witness = rng.sample(range(10), 4)
    i, j = rng.sample(range(4), 2)
    if witness[i] < witness[j]:
        i, j = j, i
    domains = []
    for digit in witness:
        others = [v for v in range(10) if v != digit]
        domains.append(tuple(sorted([digit] + rng.sample(others, sizes[difficulty] - 1))))
    return Puzzle(tuple(domains), sum(witness), (i, j), True, revision)


def change_rules(puzzle, *, total=None, greater=None):
    """New immutable revision; may be unsatisfiable, which solve reports safely."""
    return Puzzle(puzzle.domains, puzzle.total if total is None else total,
                  puzzle.greater if greater is None else greater,
                  puzzle.all_different, puzzle.revision + 1)
