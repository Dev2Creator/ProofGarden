"""Cross-check the DPLL SAT solver against exhaustive truth-table enumeration.

Two independent implementations must agree on every randomly generated small
formula. Enumeration is exponential, so the generator stays at four variables
or fewer; that is enough to catch encoding bugs, polarity mistakes, and
unsound unit propagation.
"""

from __future__ import annotations

import itertools
import random
import unittest

from proofgarden.logic.ast import BinOp, Const, Not, Var
from proofgarden.logic.sat import solve
from proofgarden.logic.truth import evaluate


def random_formula(rng: random.Random, variables, depth: int = 0):
    """Build a random formula over ``variables`` with bounded depth."""
    if depth >= 3 or rng.random() < 0.3:
        if rng.random() < 0.15:
            return Const(rng.random() < 0.5)
        return Var(rng.choice(variables))
    kind = rng.choice(["not", "binop"])
    if kind == "not":
        return Not(random_formula(rng, variables, depth + 1))
    op = rng.choice(["AND", "OR", "XOR", "IMPLIES", "IFF"])
    return BinOp(op, random_formula(rng, variables, depth + 1), random_formula(rng, variables, depth + 1))


def enumerate_satisfiable(formula, variables) -> bool:
    if not variables:
        return evaluate(formula, {})
    for values in itertools.product([False, True], repeat=len(variables)):
        assignment = dict(zip(variables, values))
        if evaluate(formula, assignment):
            return True
    return False


class TestSatCrossCheck(unittest.TestCase):
    def test_random_formulas_agree_with_enumeration(self):
        rng = random.Random(20260101)
        variables = ["P", "Q", "R", "S"]
        checked = 0
        for _ in range(400):
            formula = random_formula(rng, variables)
            free = sorted(formula.variables())
            expected = enumerate_satisfiable(formula, free)
            actual = solve(formula).satisfiable
            self.assertEqual(
                actual,
                expected,
                msg=f"solver disagrees with enumeration on: {formula}",
            )
            checked += 1
        self.assertEqual(checked, 400)

    def test_model_returned_by_solver_satisfies_formula(self):
        rng = random.Random(7)
        variables = ["P", "Q", "R"]
        for _ in range(150):
            formula = random_formula(rng, variables)
            result = solve(formula)
            if result.satisfiable:
                self.assertTrue(
                    evaluate(formula, result.assignment),
                    msg=f"reported model does not satisfy: {formula}",
                )

    def test_unsatisfiable_core_examples(self):
        for text in ["P AND NOT P", "(P OR Q) AND NOT P AND NOT Q"]:
            from proofgarden.logic.parser import parse

            self.assertFalse(solve(parse(text)).satisfiable, msg=text)

    def test_tautology_is_satisfiable_but_negation_is_not(self):
        from proofgarden.logic.parser import parse

        self.assertTrue(solve(parse("P OR NOT P")).satisfiable)
        self.assertFalse(solve(parse("NOT (P OR NOT P)")).satisfiable)


if __name__ == "__main__":
    unittest.main()
