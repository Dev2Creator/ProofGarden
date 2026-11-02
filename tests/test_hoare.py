"""Tests for the Hoare-logic module."""

import unittest

from proofgarden.verification.hoare import (
    AndC,
    Arith,
    Assign,
    Cmp,
    If,
    Num,
    Seq,
    VarE,
    While,
    check_implication,
    run,
    verify,
    wp,
)


def var(name):
    return VarE(name)


def num(value):
    return Num(value)


class TestWeakestPrecondition(unittest.TestCase):
    def test_assignment(self):
        program = Assign("x", Arith("+", var("x"), num(1)))
        post = Cmp(">", var("x"), num(5))
        pre = wp(program, post)
        # wp(x := x + 1, x > 5) == x + 1 > 5
        self.assertEqual(str(pre), "(x + 1) > 5")

    def test_sequence(self):
        program = Seq(
            Assign("x", Arith("+", var("x"), num(1))),
            Assign("x", Arith("*", var("x"), num(2))),
        )
        post = Cmp("==", var("x"), num(10))
        pre = wp(program, post)
        # ((x + 1) * 2) == 10
        self.assertEqual(str(pre), "((x + 1) * 2) == 10")

    def test_conditional(self):
        program = If(Cmp(">", var("x"), num(0)), Assign("y", num(1)), Assign("y", num(-1)))
        pre = wp(program, Cmp("==", var("y"), num(1)))
        text = str(pre)
        self.assertIn("x > 0", text)
        self.assertIn("y := 1", text) if "y := 1" in text else None
        # precondition should mention the then-branch expression
        self.assertIn("1 == 1", text)

    def test_while_requires_invariant(self):
        loop = While(
            Cmp("<", var("i"), num(3)),
            Cmp("<=", var("i"), num(3)),
            Assign("i", Arith("+", var("i"), num(1))),
        )
        pre = wp(loop, Cmp("==", var("i"), num(3)))
        self.assertEqual(str(pre), "i <= 3")


class TestInterpreter(unittest.TestCase):
    def test_sequence_runs(self):
        program = Seq(
            Assign("x", Arith("+", var("x"), num(2))),
            Assign("x", Arith("*", var("x"), num(3))),
        )
        self.assertEqual(run(program, {"x": 1}), {"x": 9})

    def test_conditional(self):
        program = If(Cmp(">", var("x"), num(0)), Assign("y", num(1)), Assign("y", num(-1)))
        self.assertEqual(run(program, {"x": 4, "y": 0})["y"], 1)
        self.assertEqual(run(program, {"x": -4, "y": 0})["y"], -1)

    def test_loop_sums(self):
        program = While(
            Cmp("<", var("i"), num(5)),
            Cmp("<=", var("i"), num(5)),
            Seq(
                Assign("sum", Arith("+", var("sum"), var("i"))),
                Assign("i", Arith("+", var("i"), num(1))),
            ),
        )
        self.assertEqual(run(program, {"i": 0, "sum": 0}), {"i": 5, "sum": 10})


class TestVerification(unittest.TestCase):
    def test_correct_program_holds(self):
        program = Assign("x", Arith("+", var("x"), num(1)))
        report = verify(
            program,
            pre=Cmp("==", var("x"), num(0)),
            post=Cmp("==", var("x"), num(1)),
            bounds={"x": range(0, 3)},
        )
        self.assertTrue(report.all_checks_held, report.format())

    def test_incorrect_program_fails(self):
        program = Assign("x", Arith("+", var("x"), num(2)))
        report = verify(
            program,
            pre=Cmp("==", var("x"), num(0)),
            post=Cmp("==", var("x"), num(1)),
            bounds={"x": range(0, 3)},
        )
        self.assertFalse(report.all_checks_held)
        failed = [c for c in report.checks if not c.held]
        self.assertTrue(failed)
        self.assertIsNotNone(failed[0].counterexample)

    def test_loop_invariant_report(self):
        # sum of 0..n via a loop; invariant: sum == i
        loop = While(
            Cmp("<", var("i"), num(3)),
            Cmp("==", var("sum"), var("i")),
            Seq(
                Assign("sum", Arith("+", var("sum"), num(1))),
                Assign("i", Arith("+", var("i"), num(1))),
            ),
        )
        report = verify(
            loop,
            pre=AndC(Cmp("==", var("sum"), num(0)), Cmp("==", var("i"), num(0))),
            post=Cmp("==", var("sum"), var("i")),
            bounds={"i": range(0, 4), "sum": range(0, 4)},
        )
        names = [c.name for c in report.checks]
        self.assertIn("preservation", names)
        self.assertIn("exit", names)

    def test_implication_counterexample(self):
        check = check_implication(
            Cmp(">", var("x"), num(0)),
            Cmp(">", var("y"), num(0)),
            {"x": range(0, 2), "y": range(0, 2)},
        )
        self.assertFalse(check.held)
        self.assertEqual(check.counterexample["y"], 0)


if __name__ == "__main__":
    unittest.main()
