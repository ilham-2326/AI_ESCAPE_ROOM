import unittest
from csp_solver import Puzzle, solve, change_rules
from keypad import KeypadController

class KeypadTests(unittest.TestCase):
    def test_key_and_current_solution_required(self):
        k=KeypadController()
        r=k.solve_current()
        self.assertFalse(k.can_unlock(True))
        self.assertTrue(k.submit(r.code,r.revision))
        self.assertFalse(k.can_unlock(False))
        self.assertTrue(k.can_unlock(True))
        self.assertFalse(k.submit('xxxx',r.revision))
        self.assertFalse(k.can_unlock(True))

    def test_rules_invalidate_result(self):
        k=KeypadController()
        old=k.solve_current()
        k.submit(old.code,old.revision)
        k.update_rules(change_rules(k.puzzle,total=21))
        self.assertIsNone(k.result)
        self.assertFalse(k.can_unlock(True))
        self.assertFalse(k.submit(old.code,old.revision))
        new=k.solve_current()
        self.assertTrue(k.submit(new.code,new.revision))
        self.assertTrue(k.can_unlock(True))

    def test_impossible_and_stale_revision(self):
        k=KeypadController()
        with self.assertRaises(ValueError):
            k.update_rules(Puzzle())
        k.update_rules(change_rules(k.puzzle,total=100))
        r=k.solve_current()
        self.assertEqual(r.status,'unsatisfiable')
        self.assertFalse(k.submit(r.code,r.revision))
        self.assertFalse(k.can_unlock(True))

    def test_mutable_inputs_detached(self):
        domains=[list(range(10)) for _ in range(4)]
        greater=[0,2]
        p=Puzzle(domains,20,greater)
        domains[0].clear()
        greater.reverse()
        self.assertEqual(len(p.domains[0]),10)
        self.assertEqual(p.greater,(0,2))
        self.assertEqual(solve(p).status,'solved')

if __name__=='__main__':
    unittest.main(verbosity=2)
