"""Member 4: frame-by-frame FSM integrating environment, search and keypad."""
from dataclasses import replace
from enum import Enum, auto
from search import plan, path_still_valid, path_cost, MAX_PATIENCE, WAIT_TOLERANCE
from keypad import KeypadController
from csp_solver import solve, Puzzle

class State(Enum):
    FIND_KEY = auto()
    GO_TO_TERMINAL = auto()
    SOLVE_PUZZLE = auto()
    GO_TO_DOOR = auto()
    GO_TO_EXIT = auto()
    ESCAPED = auto()
    FAILED = auto()

class Agent:
    def __init__(self, env, algorithm='astar'):
        self.env = env
        self.algorithm = algorithm
        self.keypad = KeypadController()
        self.reset()

    def reset(self):
        self.env.reset()
        self.keypad = KeypadController()
        self.pos = self.env.start
        self.state = State.FIND_KEY
        self.has_key = False
        self.door_approach = None
        self.step_count = 0
        self.path = None
        self.path_index = 1
        self.explored = set()
        self.nodes_expanded = 0
        self.replans = 0
        self.waits = 0
        self.consecutive_waits = 0
        self.path_cost_total = 0
        self.last_event = 'Ready'
        self._plan()

    def _goal(self):
        return {State.FIND_KEY:self.env.key_pos,
                State.GO_TO_TERMINAL:self.env.terminal_pos,
                State.GO_TO_DOOR:self.door_approach,
                State.GO_TO_EXIT:self.env.exit}.get(self.state)

    def _plan(self, replan=False, ignore_guards=True):
        # The locked door is impassable. Find a reachable floor tile adjacent
        # to it, then unlock the door from there (not from inside the door).
        if self.state == State.GO_TO_DOOR:
            r, c = self.env.door_pos
            candidates = [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]
            options = []
            for cell in candidates:
                if not self.env.in_bounds(cell) or self.env.is_wall(cell):
                    continue
                route, st = plan(self.env, self.pos, cell, self.algorithm,
                                 ignore_obstacles=True)
                if route is not None:
                    options.append((st['path_cost'], len(route), cell))
            self.door_approach = min(options)[2] if options else None
        goal = self._goal()
        if goal is None:
            self.path = None
            return
        self.path, stats, explored = plan(
            self.env, self.pos, goal, self.algorithm,
            ignore_obstacles=ignore_guards, return_explored=True)
        self.path_index = 1
        self.explored = explored
        self.nodes_expanded += stats['nodes_expanded']
        if replan:
            self.replans += 1
        if self.path is None:
            self.last_event = 'No route currently available'

    def _change_rules(self):
        old = self.keypad.puzzle
        # Deterministic, explicitly defined new constraint; select a solvable total.
        for total in (old.total + 1, old.total - 1, old.total + 2, old.total - 2):
            if total < 0:
                continue
            candidate = replace(old, total=total, revision=old.revision + 1)
            if solve(candidate).status == 'solved':
                self.keypad.update_rules(candidate)
                self.env.door_open = False
                # Only send the agent back to re-solve if it already has the key;
                # otherwise it must keep looking for the key first.
                if self.has_key:
                    self.state = State.GO_TO_TERMINAL
                self._plan()
                self.last_event = f'Puzzle rules updated (sum={total}); solve again'
                return
        self.state = State.FAILED
        self.last_event = 'No solvable revised puzzle available'

    def _arrived(self):
        if self.state == State.FIND_KEY:
            self.has_key = True
            self.state = State.GO_TO_TERMINAL
            self.last_event = 'Key collected'
            self._plan()
        elif self.state == State.GO_TO_TERMINAL:
            self.state = State.SOLVE_PUZZLE
            self.path = None
        elif self.state == State.GO_TO_DOOR:
            if self.keypad.can_unlock(self.has_key):
                self.env.door_open = True
                self.state = State.GO_TO_EXIT
                self.last_event = 'Door unlocked'
                self._plan()
            else:
                self.state = State.GO_TO_TERMINAL
                self._plan()
        elif self.state == State.GO_TO_EXIT:
            self.state = State.ESCAPED
            self.path = None
            self.last_event = 'Escaped successfully!'

    def update(self):
        """Exactly one simulation tick; call from Pygame timer, never per render frame."""
        if self.state in (State.ESCAPED, State.FAILED):
            return
        self.step_count += 1
        events = self.env.tick(self.step_count, self.pos)
        for event in events:
            if event.kind == 'rule_changed':
                self._change_rules()
            elif event.kind == 'route_blocked':
                self.last_event = 'Corridor collapsed; checking route'
        if self.state == State.FAILED:
            return
        if self.state == State.SOLVE_PUZZLE:
            result = self.keypad.solve_current()
            if result.status == 'solved' and self.keypad.submit(result.code, result.revision):
                self.state = State.GO_TO_DOOR
                self.last_event = 'Keypad solved'
                self._plan()
            else:
                self.state = State.FAILED
                self.last_event = 'Puzzle unsolvable'
            return
        goal = self._goal()
        if self.pos == goal:
            self._arrived()
            return
        if self.path is None or not path_still_valid(
                self.env, self.path, self.path_index, ignore_obstacles=True):
            self._plan(replan=True)
        if self.path is None:
            self.waits += 1
            return
        next_pos = self.path[self.path_index]
        if self.env.is_blocked(next_pos):
            detour, stats = plan(self.env, self.pos, goal, self.algorithm)
            self.nodes_expanded += stats['nodes_expanded']
            remaining = self.path[self.path_index - 1:]
            extra = (path_cost(self.env, detour) - path_cost(self.env, remaining)
                     if detour else None)
            if detour and (extra <= WAIT_TOLERANCE or self.consecutive_waits >= MAX_PATIENCE):
                self.path = detour
                self.path_index = 1
                self.replans += 1
                self.consecutive_waits = 0
                next_pos = self.path[self.path_index]
            else:
                self.waits += 1
                self.consecutive_waits += 1
                self.last_event = 'Waiting for moving obstacle'
                return
        if self.env.is_blocked(next_pos):
            self.waits += 1
            return
        self.pos = next_pos
        self.path_cost_total += self.env.cost(self.pos)
        self.path_index += 1
        self.consecutive_waits = 0
        if self.pos == goal:
            self._arrived()
