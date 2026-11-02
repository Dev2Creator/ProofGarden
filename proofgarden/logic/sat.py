"""A small, honest DPLL SAT solver for propositional formulas.

Pipeline: formula AST -> NNF -> Tseitin CNF -> DPLL with unit propagation
and pure-literal elimination.

This is an educational solver. It is correct for the formulas it accepts but
it is not a competitive SAT solver: there is no clause learning, no watched
literals and no heuristics tuning.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

from .ast import BinOp, Const, Expr, Not, Var

Clause = Tuple[int, ...]


class _Encoder:
    """Tseitin encoder producing an equisatisfiable CNF."""

    def __init__(self) -> None:
        self.clauses: List[Clause] = []
        self.next_var = 1
        self.var_of_atom: Dict[str, int] = {}

    def fresh(self) -> int:
        v = self.next_var
        self.next_var += 1
        return v

    def atom(self, name: str) -> int:
        if name not in self.var_of_atom:
            self.var_of_atom[name] = self.fresh()
        return self.var_of_atom[name]

    def encode(self, expr: Expr, negated: bool = False) -> int:
        if isinstance(expr, Const):
            t = self.fresh()
            self.clauses.append((t,) if expr.value != negated else (-t,))
            return t
        if isinstance(expr, Var):
            lit = self.atom(expr.name)
            return -lit if negated else lit
        if isinstance(expr, Not):
            return self.encode(expr.operand, not negated)
        if isinstance(expr, BinOp):
            if expr.op == "AND":
                a = self.encode(expr.left, negated)
                b = self.encode(expr.right, negated)
                # negated AND == OR of negations; encode via a fresh gate
                return self._or_gate(a, b) if negated else self._and_gate(a, b)
            if expr.op == "OR":
                a = self.encode(expr.left, negated)
                b = self.encode(expr.right, negated)
                return self._and_gate(a, b) if negated else self._or_gate(a, b)
            if expr.op == "IMPLIES":
                # A -> B  ==  ~A or B
                return self.encode(BinOp("OR", Not(expr.left), expr.right), negated)
            if expr.op == "IFF":
                return self.encode(
                    BinOp(
                        "AND",
                        BinOp("IMPLIES", expr.left, expr.right),
                        BinOp("IMPLIES", expr.right, expr.left),
                    ),
                    negated,
                )
            if expr.op == "XOR":
                return self.encode(
                    BinOp(
                        "AND",
                        BinOp("OR", expr.left, expr.right),
                        Not(BinOp("AND", expr.left, expr.right)),
                    ),
                    negated,
                )
        raise TypeError(f"unsupported node {type(expr).__name__}")

    def _and_gate(self, a: int, b: int) -> int:
        t = self.fresh()
        self.clauses += [(-t, a), (-t, b), (t, -a, -b)]
        return t

    def _or_gate(self, a: int, b: int) -> int:
        t = self.fresh()
        self.clauses += [(t, -a), (t, -b), (-t, a, b)]
        return t


def to_cnf(expr: Expr) -> Tuple[List[Clause], Dict[str, int]]:
    """Encode ``expr`` into CNF. Returns (clauses, atom->solver var map)."""
    enc = _Encoder()
    root = enc.encode(expr)
    enc.clauses.append((root,))
    return enc.clauses, enc.var_of_atom


def _simplify(clauses: List[Clause], assignment: Dict[int, bool]) -> Optional[List[Clause]]:
    result: List[Clause] = []
    for clause in clauses:
        new_clause: List[int] = []
        satisfied = False
        for lit in clause:
            var = abs(lit)
            if var in assignment:
                if assignment[var] == (lit > 0):
                    satisfied = True
                    break
            else:
                new_clause.append(lit)
        if satisfied:
            continue
        if not new_clause:
            return None  # empty clause: conflict
        result.append(tuple(new_clause))
    return result


def _dpll(clauses: List[Clause], assignment: Dict[int, bool]) -> Optional[Dict[int, bool]]:
    simplified = _simplify(clauses, assignment)
    if simplified is None:
        return None
    if not simplified:
        return assignment

    # unit propagation
    for clause in simplified:
        if len(clause) == 1:
            lit = clause[0]
            new_assignment = dict(assignment)
            new_assignment[abs(lit)] = lit > 0
            return _dpll(simplified, new_assignment)

    # pure literal elimination
    polarities: Dict[int, set] = {}
    for clause in simplified:
        for lit in clause:
            polarities.setdefault(abs(lit), set()).add(lit > 0)
    for var, signs in polarities.items():
        if len(signs) == 1:
            new_assignment = dict(assignment)
            new_assignment[var] = signs.pop()
            return _dpll(simplified, new_assignment)

    # branch on the most frequent variable
    counts: Dict[int, int] = {}
    for clause in simplified:
        for lit in clause:
            counts[abs(lit)] = counts.get(abs(lit), 0) + 1
    var = max(counts, key=counts.get)

    for value in (True, False):
        new_assignment = dict(assignment)
        new_assignment[var] = value
        result = _dpll(simplified, new_assignment)
        if result is not None:
            return result
    return None


@dataclass(frozen=True)
class SatResult:
    satisfiable: bool
    assignment: Optional[Dict[str, bool]]


def solve(expr: Expr) -> SatResult:
    """Decide satisfiability and return a model over the original variables."""
    clauses, atom_vars = to_cnf(expr)
    model = _dpll(clauses, {})
    if model is None:
        return SatResult(False, None)
    assignment = {name: model.get(var, False) for name, var in atom_vars.items()}
    return SatResult(True, assignment)
