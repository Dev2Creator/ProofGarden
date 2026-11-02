"""Tests for the propositional logic engine."""

import unittest

from proofgarden.logic.lexer import LexError
from proofgarden.logic.parser import ParseError, parse
from proofgarden.logic.sat import solve
from proofgarden.logic.truth import check_equivalent, evaluate, truth_table


class TestTruthTables(unittest.TestCase):
    def test_implication_is_tautology(self):
        table = truth_table(parse("(P AND Q) IMPLIES P"))
        self.assertEqual(table.classification, "tautology")
        self.assertEqual(len(table.rows), 4)

    def test_contradiction(self):
        self.assertEqual(truth_table(parse("P AND NOT P")).classification, "contradiction")

    def test_contingent(self):
        self.assertEqual(truth_table(parse("P AND Q")).classification, "contingent")

    def test_xor_semantics(self):
        expr = parse("P XOR Q")
        self.assertTrue(evaluate(expr, {"P": True, "Q": False}))
        self.assertFalse(evaluate(expr, {"P": True, "Q": True}))

    def test_iff_semantics(self):
        expr = parse("P IFF Q")
        self.assertTrue(evaluate(expr, {"P": False, "Q": False}))
        self.assertFalse(evaluate(expr, {"P": True, "Q": False}))

    def test_variable_casing_preserved(self):
        table = truth_table(parse("alpha AND beta"))
        self.assertEqual(table.names, ("alpha", "beta"))


class TestPrecedence(unittest.TestCase):
    def test_and_binds_tighter_than_or(self):
        expr = parse("P OR Q AND R")
        # P OR (Q AND R): true when P alone is true
        self.assertTrue(evaluate(expr, {"P": True, "Q": False, "R": False}))
        # Q AND R is false here, and P is false
        self.assertFalse(evaluate(expr, {"P": False, "Q": True, "R": False}))

    def test_not_binds_tightest(self):
        expr = parse("NOT P AND Q")
        self.assertFalse(evaluate(expr, {"P": True, "Q": True}))

    def test_implication_right_associative(self):
        # A IMPLIES B IMPLIES C == A IMPLIES (B IMPLIES C)
        expr = parse("A IMPLIES B IMPLIES C")
        env = {"A": True, "B": False, "C": False}
        # B -> C is true, so A -> (B -> C) is true
        self.assertTrue(evaluate(expr, env))

    def test_parentheses_override(self):
        expr = parse("(P OR Q) AND R")
        self.assertFalse(evaluate(expr, {"P": True, "Q": False, "R": False}))


class TestErrors(unittest.TestCase):
    def test_missing_operand(self):
        with self.assertRaises(ParseError):
            parse("P AND")

    def test_unbalanced_parentheses(self):
        with self.assertRaises(ParseError):
            parse("((P AND Q)")

    def test_illegal_character(self):
        with self.assertRaises(LexError):
            parse("P # Q")

    def test_empty_input(self):
        with self.assertRaises(ParseError):
            parse("   ")

    def test_no_python_execution(self):
        # A call expression such as __import__('os') must not be executable.
        with self.assertRaises((ParseError, LexError)):
            parse("__import__('os')")

    def test_unknown_variable_raises(self):
        with self.assertRaises(KeyError):
            evaluate(parse("P AND Q"), {"P": True})


class TestEquivalence(unittest.TestCase):
    def test_de_morgan(self):
        result = check_equivalent(parse("NOT (P AND Q)"), parse("(NOT P) OR (NOT Q)"))
        self.assertTrue(result.equivalent)

    def test_distribution(self):
        result = check_equivalent(
            parse("P AND (Q OR R)"),
            parse("(P AND Q) OR (P AND R)"),
        )
        self.assertTrue(result.equivalent)

    def test_non_equivalent_has_counterexample(self):
        result = check_equivalent(parse("P IMPLIES Q"), parse("Q IMPLIES P"))
        self.assertFalse(result.equivalent)
        self.assertIsNotNone(result.counterexample)
        env = result.counterexample
        self.assertTrue(env["P"] and not env["Q"] or env["Q"] and not env["P"])


class TestSat(unittest.TestCase):
    def test_contradiction_unsatisfiable(self):
        self.assertFalse(solve(parse("P AND NOT P")).satisfiable)

    def test_simple_model(self):
        result = solve(parse("(P OR Q) AND NOT P"))
        self.assertTrue(result.satisfiable)
        self.assertFalse(result.assignment["P"])
        self.assertTrue(result.assignment["Q"])

    def test_implication_chain(self):
        expr = parse("(A IMPLIES B) AND A AND NOT B")
        self.assertFalse(solve(expr).satisfiable)

    def test_model_satisfies_formula(self):
        expr = parse("(A OR B) AND (NOT A OR C) AND (NOT B OR C)")
        result = solve(expr)
        self.assertTrue(result.satisfiable)
        self.assertTrue(evaluate(expr, result.assignment))


if __name__ == "__main__":
    unittest.main()
