"""CLI and example regression tests."""

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cli(*args, expect=0):
    result = subprocess.run(
        [sys.executable, "-m", "proofgarden", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == expect, (
        f"exit {result.returncode} for {args}\nstdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return result


class TestCli(unittest.TestCase):
    def test_help(self):
        result = cli("--help")
        self.assertIn("proofgarden", result.stdout)

    def test_truth_table_json(self):
        result = cli("logic", "truth-table", "(P AND Q) IMPLIES P", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["classification"], "tautology")
        self.assertEqual(len(payload["rows"]), 4)

    def test_classify(self):
        result = cli("logic", "classify", "P OR NOT P")
        self.assertIn("tautology", result.stdout)

    def test_equivalence_exit_code(self):
        cli("logic", "equiv", "NOT (P AND Q)", "(NOT P) OR (NOT Q)")
        result = cli("logic", "equiv", "P", "Q", expect=1)
        self.assertIn("NOT logically equivalent", result.stdout)

    def test_sat_json(self):
        result = cli("logic", "sat", "P AND NOT P", "--json")
        payload = json.loads(result.stdout)
        self.assertFalse(payload["satisfiable"])

    def test_invalid_expression(self):
        result = cli("logic", "truth-table", "P AND", expect=2)
        self.assertIn("error", result.stderr.lower())

    def test_system_info(self):
        result = cli("system", "info", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["name"], "ProofGarden")

    def test_examples_list(self):
        result = cli("examples", "list", "--json")
        payload = json.loads(result.stdout)
        self.assertIn("traffic_light.json", payload["examples"])


class TestDocumentedExamples(unittest.TestCase):
    """Each example must produce the outcome its description promises."""

    def run_model(self, name):
        result = cli("modelcheck", f"{name}.json", "--json")
        return json.loads(result.stdout)

    def test_traffic_light_verifies(self):
        payload = self.run_model("traffic_light")
        self.assertTrue(payload["exploration_complete"])
        outcomes = {c["property"]: c["outcome"] for c in payload["checks"]}
        self.assertEqual(outcomes["invariant: no_undefined_signal"], "verified")

    def test_counter_overflow_fails_with_trace(self):
        payload = self.run_model("counter_overflow")
        failed = [c for c in payload["checks"] if c["outcome"] == "violated"]
        self.assertEqual(len(failed), 1)
        trace = failed[0]["trace"]["steps"]
        self.assertEqual([step["state"]["count"] for step in trace], [0, 1, 2, 3, 4])

    def test_deadlock_example(self):
        payload = self.run_model("deadlock_locks")
        outcomes = {c["property"]: c["outcome"] for c in payload["checks"]}
        self.assertEqual(outcomes["deadlock freedom"], "violated")
        self.assertTrue(payload["deadlocks"])

    def test_bank_withdrawal_violates(self):
        payload = self.run_model("bank_withdrawal")
        outcomes = {c["property"]: c["outcome"] for c in payload["checks"]}
        self.assertEqual(outcomes["invariant: balance_never_negative"], "violated")


if __name__ == "__main__":
    unittest.main()
