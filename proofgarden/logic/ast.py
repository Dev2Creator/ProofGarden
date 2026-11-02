"""Abstract syntax for propositional formulas.

Deliberately small and explicit: no Python ``eval`` is ever used to
interpret user input.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Tuple, Union


class Expr:
    """Base class for formula nodes."""

    def variables(self) -> FrozenSet[str]:
        raise NotImplementedError


@dataclass(frozen=True)
class Var(Expr):
    name: str

    def variables(self) -> FrozenSet[str]:
        return frozenset({self.name})

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Const(Expr):
    value: bool

    def variables(self) -> FrozenSet[str]:
        return frozenset()

    def __str__(self) -> str:
        return "TRUE" if self.value else "FALSE"


@dataclass(frozen=True)
class Not(Expr):
    operand: Expr

    def variables(self) -> FrozenSet[str]:
        return self.operand.variables()

    def __str__(self) -> str:
        return f"NOT {self.operand}"


BINARY_OPS = ("AND", "OR", "XOR", "IMPLIES", "IFF")


@dataclass(frozen=True)
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr

    def __post_init__(self) -> None:
        if self.op not in BINARY_OPS:
            raise ValueError(f"unknown operator: {self.op}")

    def variables(self) -> FrozenSet[str]:
        return self.left.variables() | self.right.variables()

    def __str__(self) -> str:
        return f"({self.left} {self.op} {self.right})"


Formula = Union[Var, Const, Not, BinOp]


def variables_of(expr: Formula) -> Tuple[str, ...]:
    """Return the free variables of ``expr`` in deterministic order."""
    return tuple(sorted(expr.variables()))
