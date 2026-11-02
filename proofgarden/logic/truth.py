"""Evaluation and truth-table tools for propositional formulas."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterator, List, Mapping, Optional, Sequence, Tuple

from .ast import BinOp, Const, Expr, Not, Var, variables_of


class UnknownVariable(KeyError):
    """Raised when an assignment omits a variable used by the formula."""


def evaluate(expr: Expr, assignment: Mapping[str, bool]) -> bool:
    """Evaluate ``expr`` under ``assignment``.

    Raises :class:`UnknownVariable` if a free variable is missing, so that a
    typo never silently evaluates to a default value.
    """
    if isinstance(expr, Const):
        return expr.value
    if isinstance(expr, Var):
        if expr.name not in assignment:
            raise UnknownVariable(expr.name)
        return bool(assignment[expr.name])
    if isinstance(expr, Not):
        return not evaluate(expr.operand, assignment)
    if isinstance(expr, BinOp):
        left = evaluate(expr.left, assignment)
        if expr.op == "AND":
            return left and evaluate(expr.right, assignment)
        if expr.op == "OR":
            return left or evaluate(expr.right, assignment)
        if expr.op == "XOR":
            return left != evaluate(expr.right, assignment)
        if expr.op == "IMPLIES":
            return (not left) or evaluate(expr.right, assignment)
        if expr.op == "IFF":
            return left == evaluate(expr.right, assignment)
    raise TypeError(f"unsupported expression node: {type(expr).__name__}")


def assignments(names: Sequence[str]) -> Iterator[Dict[str, bool]]:
    for values in product((False, True), repeat=len(names)):
        yield dict(zip(names, values))


@dataclass(frozen=True)
class TruthTable:
    expr: Expr
    names: Tuple[str, ...]
    rows: Tuple[Tuple[Dict[str, bool], bool], ...]

    @property
    def classification(self) -> str:
        values = {value for _, value in self.rows}
        if values == {True}:
            return "tautology"
        if values == {False}:
            return "contradiction"
        return "contingent"


def truth_table(expr: Expr, max_variables: int = 16) -> TruthTable:
    names = variables_of(expr)
    if len(names) > max_variables:
        raise ValueError(
            f"{len(names)} variables exceeds the truth-table limit of {max_variables}"
        )
    rows = tuple((a, evaluate(expr, a)) for a in assignments(names))
    return TruthTable(expr=expr, names=names, rows=rows)


def is_tautology(expr: Expr) -> bool:
    return truth_table(expr).classification == "tautology"


def is_satisfiable(expr: Expr) -> bool:
    return any(value for _, value in truth_table(expr).rows)


@dataclass(frozen=True)
class EquivalenceResult:
    equivalent: bool
    counterexample: Optional[Dict[str, bool]]


def check_equivalent(left: Expr, right: Expr) -> EquivalenceResult:
    """Compare two formulas over the union of their variables."""
    names = tuple(sorted(left.variables() | right.variables()))
    if len(names) > 16:
        raise ValueError("too many variables for exhaustive equivalence checking")
    for assignment in assignments(names):
        if evaluate(left, assignment) != evaluate(right, assignment):
            return EquivalenceResult(False, assignment)
    return EquivalenceResult(True, None)


def format_truth_table(table: TruthTable) -> str:
    """Render a truth table as aligned plain text."""
    headers = list(table.names) + ["RESULT"]
    widths = [max(len(h), 5) for h in headers]
    lines = [" | ".join(h.ljust(w) for h, w in zip(headers, widths))]
    lines.append("-+-".join("-" * w for w in widths))
    for assignment, value in table.rows:
        cells = ["TRUE" if assignment[n] else "FALSE" for n in table.names]
        cells.append("TRUE" if value else "FALSE")
        lines.append(" | ".join(c.ljust(w) for c, w in zip(cells, widths)))
    return "\n".join(lines)
