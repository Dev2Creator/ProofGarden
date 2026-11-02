"""Tests for state systems and the bounded model checker."""

import unittest

from proofgarden.modelchecking.explorer import Explorer
from proofgarden.state import StateSystem, Transition, make_state, system_from_python


def counter_system(max_value=3):
    """A counter that increments up to ``max_value`` plus one bad step."""

    def inc_guard(state):
        return dict(state)["n"] < max_value + 1

    def inc_action(state):
        return make_state({"n": dict(state)["n"] + 1})

    return system_from_python(
        "counter",
        initial=[{"n": 0}],
        transitions=[("inc", inc_guard, inc_action)],
    )


class TestStateSystem(unittest.TestCase):
    def test_requires_initial_state(self):
        with self.assertRaises(ValueError):
            StateSystem(name="x", initial_states=(), transitions=(Transition("t", lambda s: True, lambda s: s),))

    def test_requires_transition(self):
        with self.assertRaises(ValueError):
            StateSystem(name="x", initial_states=(make_state({"n": 0}),), transitions=())

    def test_successors(self):
        system = counter_system()
        successors = system.successors(make_state({"n": 0}))
        self.assertEqual(len(successors), 1)
        self.assertEqual(dict(successors[0][1])["n"], 1)


class TestExploration(unittest.TestCase):
    def test_explores_whole_finite_system(self):
        explored = Explorer(counter_system()).explore()
        self.assertTrue(explored.complete)
        self.assertEqual(len(explored.states), 5)  # 0..4

    def test_max_states_gives_incomplete(self):
        result = Explorer(counter_system(), max_states=2).explore()
        self.assertFalse(result.complete)
        self.assertIn("state limit", result.stop_reason)

    def test_depth_limit(self):
        result = Explorer(counter_system(), max_depth=1).explore()
        self.assertFalse(result.complete)
        self.assertIn("depth limit", result.stop_reason)

    def test_incomplete_never_reports_verified(self):
        explorer = Explorer(counter_system(), max_states=2)
        check = explorer.check_invariant("n >= 0", lambda s: dict(s)["n"] < 0)
        self.assertEqual(check.outcome, "incomplete")


class TestChecks(unittest.TestCase):
    def test_invariant_violation_trace(self):
        explorer = Explorer(counter_system())
        check = explorer.check_invariant("n <= 3", lambda s: dict(s)["n"] > 3)
        self.assertEqual(check.outcome, "violated")
        self.assertIsNotNone(check.trace)
        states = [step.state["n"] for step in check.trace.steps]
        self.assertEqual(states, [0, 1, 2, 3, 4])

    def test_invariant_holds(self):
        explorer = Explorer(counter_system())
        check = explorer.check_invariant("n >= 0", lambda s: dict(s)["n"] < 0)
        self.assertEqual(check.outcome, "verified")

    def test_reachability_found(self):
        explorer = Explorer(counter_system())
        check = explorer.check_reachability("n == 3", lambda s: dict(s)["n"] == 3)
        self.assertEqual(check.outcome, "verified")
        self.assertEqual(check.trace.steps[-1].state["n"], 3)

    def test_reachability_unreachable(self):
        explorer = Explorer(counter_system())
        check = explorer.check_reachability("n == 99", lambda s: dict(s)["n"] == 99)
        self.assertEqual(check.outcome, "violated")
        self.assertIsNone(check.trace)

    def test_deadlock_detection(self):
        def lock_system():
            def guard_a(state):
                return dict(state)["a"] == "free"

            def take_a(state):
                return make_state({"a": "held", "b": dict(state)["b"]})

            return system_from_python(
                "locks",
                initial=[{"a": "free", "b": "free"}],
                transitions=[("take_a", guard_a, take_a)],
            )

        explorer = Explorer(lock_system())
        check = explorer.check_deadlock_free()
        self.assertEqual(check.outcome, "violated")
        self.assertTrue(check.trace)

    def test_deadlock_free(self):
        # a counter that wraps around never deadlocks
        def wrap_guard(state):
            return True

        def wrap_action(state):
            return make_state({"n": (dict(state)["n"] + 1) % 3})

        system = system_from_python(
            "wrapping", initial=[{"n": 0}], transitions=[("tick", wrap_guard, wrap_action)]
        )
        check = Explorer(system).check_deadlock_free()
        self.assertEqual(check.outcome, "verified")


class TestJsonModels(unittest.TestCase):
    def test_all_examples_load(self):
        from pathlib import Path

        from proofgarden.state import load_system

        root = Path(__file__).resolve().parents[1] / "examples" / "models"
        files = sorted(root.glob("*.json"))
        self.assertGreaterEqual(len(files), 4)
        for path in files:
            system, invariants, target, deadlock = load_system(path)
            self.assertTrue(system.name)
            self.assertTrue(system.initial_states)


if __name__ == "__main__":
    unittest.main()
