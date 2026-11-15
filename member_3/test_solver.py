import itertools
import random
import unittest
from csp_solver import Puzzle, solve, validate_code, generate_puzzle, change_rules

class SolverTests(unittest.TestCase):
    def test_default(self):
        for method in ('baseline', 'optimized'):
            p = Puzzle()
            r = solve(p, method)
            self.assertTrue(validate_code(p, r.code))

    def test_generated(self):
        for level in ('easy', 'medium', 'hard'):
            for seed in range(100):
                p = generate_puzzle(seed, level)
                self.assertEqual(p, generate_puzzle(seed, level))
                for method in ('baseline', 'optimized'):
                    self.assertTrue(validate_code(p, solve(p, method).code))

    def test_oracle(self):
        rng = random.Random(7)
        for _ in range(200):
            ds = tuple(tuple(sorted(rng.sample(range(10), rng.randint(1, 4)))) for _ in range(4))
            p = Puzzle(ds, rng.randrange(37), tuple(rng.sample(range(4), 2)), rng.choice([True, False]))
            # Independent exhaustive oracle; do not reuse solver's validator.
            expected = []
            for a in itertools.product(*ds):
                if (sum(a) == p.total and (not p.all_different or len(set(a)) == 4)
                    and a[p.greater[0]] > a[p.greater[1]]):
                    expected.append(''.join(map(str, a)))
            for method in ('baseline', 'optimized'):
                r = solve(p, method)
                self.assertEqual(r.status == 'solved', bool(expected))
                if expected:
                    self.assertIn(r.code, expected)

    def test_rule_change(self):
        p = Puzzle()
        old = solve(p)
        updated = change_rules(p, total=21)
        new = solve(updated)
        self.assertEqual(new.revision, 2)
        self.assertFalse(validate_code(updated, old.code))
        self.assertTrue(validate_code(updated, new.code))
        self.assertEqual(solve(change_rules(updated, total=100)).status, 'unsatisfiable')
        self.assertEqual(p.revision, 1)

    def test_leading_zero(self):
        p = Puzzle(((0,), (9,), (1,), (8,)), 18, (1, 2))
        self.assertEqual(solve(p).code, '0918')

    def test_invalid(self):
        for ds in ((), ((),) * 4, ((10,),) * 4, ((1, 1),) * 4):
            with self.assertRaises(ValueError):
                Puzzle(ds)
        with self.assertRaises(ValueError):
            solve(Puzzle(), 'wrong')
        for code in (None, 1234, '123', 'abcd', '１２３４'):
            self.assertFalse(validate_code(Puzzle(), code))

if __name__ == '__main__':
    unittest.main(verbosity=2)
