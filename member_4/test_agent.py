
"""Member 4: Automated FSM and integration tests."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for folder in ("member_1", "member_2", "member_3", "member_4"):
    sys.path.insert(0, str(ROOT / folder))

from agent import Agent, State
from level_generator import random_level


def run_agent(agent, max_steps=1000):
    """Run the simulation until it finishes or reaches the limit."""
    for _ in range(max_steps):
        if agent.state in (State.ESCAPED, State.FAILED):
            break
        agent.update()
    return agent.state


class TestAgentIntegration(unittest.TestCase):

    def make_agent(self, seed=7, algorithm="astar"):
        env = random_level(seed=seed)
        return Agent(env, algorithm=algorithm)

    def test_initial_state(self):
        agent = self.make_agent()
        self.assertEqual(agent.state, State.FIND_KEY)
        self.assertFalse(agent.has_key)
        self.assertFalse(agent.env.door_open)

    def test_keypad_requires_key(self):
        agent = self.make_agent()
        self.assertFalse(agent.keypad.can_unlock(False))

    def test_reset(self):
        agent = self.make_agent()
        agent.update()
        agent.reset()
        self.assertEqual(agent.state, State.FIND_KEY)
        self.assertEqual(agent.step_count, 0)
        self.assertFalse(agent.has_key)

    def test_complete_escape(self):
        agent = self.make_agent()
        result = run_agent(agent)
        self.assertEqual(result, State.ESCAPED)
        self.assertTrue(agent.has_key)
        self.assertTrue(agent.keypad.can_unlock(agent.has_key))
        self.assertTrue(agent.env.door_open)
        self.assertEqual(agent.pos, agent.env.exit)

    def test_multiple_random_levels(self):
        for seed in (7, 8, 9):
            with self.subTest(seed=seed):
                agent = self.make_agent(seed=seed)
                self.assertEqual(run_agent(agent), State.ESCAPED)

    def test_all_search_algorithms(self):
        for algorithm in ("bfs", "dijkstra", "greedy", "astar"):
            with self.subTest(algorithm=algorithm):
                agent = self.make_agent(algorithm=algorithm)
                self.assertEqual(run_agent(agent), State.ESCAPED)


if __name__ == "__main__":
    unittest.main(verbosity=2)
