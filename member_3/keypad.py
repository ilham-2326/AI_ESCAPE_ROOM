"""Member 4 adapter: own one controller per keypad, process events serially."""
from csp_solver import Puzzle, solve, validate_code

class KeypadController:
    def __init__(self, puzzle=None):
        self.puzzle = puzzle if puzzle is not None else Puzzle()
        self.result = None
        self.solved = False

    def update_rules(self, puzzle):
        if puzzle.revision <= self.puzzle.revision:
            raise ValueError('Rule updates require a strictly newer revision')
        self.puzzle = puzzle
        self.result = None
        self.solved = False

    def solve_current(self, method='optimized'):
        self.result = solve(self.puzzle, method)
        self.solved = False  # solving alone must not unlock a door
        return self.result

    def submit(self, code, revision):
        self.solved = revision == self.puzzle.revision and validate_code(self.puzzle, code)
        return self.solved

    def can_unlock(self, has_key):
        return bool(has_key and self.solved)
