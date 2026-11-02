"""Educational Hoare-logic explorer.

Supported language: assignments, sequential composition, if/else, and while
loops annotated with an invariant. Weakest preconditions are computed
symbolically for assignment, composition and conditionals. For loops the
standard rule is applied: the annotated invariant is the precondition, and two
verification conditions are generated.

Verification conditions are *checked on a finite integer domain* by default.
That is a test over the sampled domain, not a proof, and the reports say so.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union


# ---------------------------------------------------------------- expressions


class Expr:
    def variables(self) -> set:
        raise NotImplementedError

    def evaluate(self, env: Dict[str, int]) -> int:
        raise NotImplementedError

    def substitute(self, name: str, value: "Expr") -> "Expr":
        raise NotImplementedError


@dataclass(frozen=True)
class Num(Expr):
    value: int

    def variables(self):
        return set()

    def evaluate(self, env):
        return self.value

    def substitute(self, name, value):
        return self

    def __str__(self):
        return str(self.value)


@dataclass(frozen=True)
class VarE(Expr):
    name: str

    def variables(self):
        return {self.name}

    def evaluate(self, env):
        if self.name not in env:
            raise KeyError(self.name)
        return env[self.name]

    def substitute(self, name, value):
        return value if self.name == name else self

    def __str__(self):
        return self.name


_ARITH = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b}


@dataclass(frozen=True)
class Arith(Expr):
    op: str
    left: Expr
    right: Expr

    def variables(self):
        return self.left.variables() | self.right.variables()

    def evaluate(self, env):
        return _ARITH[self.op](self.left.evaluate(env), self.right.evaluate(env))

    def substitute(self, name, value):
        return Arith(self.op, self.left.substitute(name, value), self.right.substitute(name, value))

    def __str__(self):
        return f"({self.left} {self.op} {self.right})"


class Cond:
    def variables(self) -> set:
        raise NotImplementedError

    def evaluate(self, env: Dict[str, int]) -> bool:
        raise NotImplementedError

    def substitute(self, name: str, value: Expr) -> "Cond":
        raise NotImplementedError


_CMP = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}


@dataclass(frozen=True)
class Cmp(Cond):
    op: str
    left: Expr
    right: Expr

    def variables(self):
        return self.left.variables() | self.right.variables()

    def evaluate(self, env):
        return _CMP[self.op](self.left.evaluate(env), self.right.evaluate(env))

    def substitute(self, name, value):
        return Cmp(self.op, self.left.substitute(name, value), self.right.substitute(name, value))

    def __str__(self):
        return f"{self.left} {self.op} {self.right}"


@dataclass(frozen=True)
class AndC(Cond):
    left: Cond
    right: Cond

    def variables(self):
        return self.left.variables() | self.right.variables()

    def evaluate(self, env):
        return self.left.evaluate(env) and self.right.evaluate(env)

    def substitute(self, name, value):
        return AndC(self.left.substitute(name, value), self.right.substitute(name, value))

    def __str__(self):
        return f"({self.left} AND {self.right})"


@dataclass(frozen=True)
class OrC(Cond):
    left: Cond
    right: Cond

    def variables(self):
        return self.left.variables() | self.right.variables()

    def evaluate(self, env):
        return self.left.evaluate(env) or self.right.evaluate(env)

    def substitute(self, name, value):
        return OrC(self.left.substitute(name, value), self.right.substitute(name, value))

    def __str__(self):
        return f"({self.left} OR {self.right})"


@dataclass(frozen=True)
class NotC(Cond):
    inner: Cond

    def variables(self):
        return self.inner.variables()

    def evaluate(self, env):
        return not self.inner.evaluate(env)

    def substitute(self, name, value):
        return NotC(self.inner.substitute(name, value))

    def __str__(self):
        return f"NOT ({self.inner})"


# ------------------------------------------------------------------- commands


class Cmd:
    def execute(self, env: Dict[str, int], steps: List[Dict[str, int]]) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class Assign(Cmd):
    name: str
    expr: Expr

    def execute(self, env, steps):
        env[self.name] = self.expr.evaluate(env)
        steps.append(dict(env))

    def __str__(self):
        return f"{self.name} := {self.expr}"


@dataclass(frozen=True)
class Seq(Cmd):
    first: Cmd
    second: Cmd

    def execute(self, env, steps):
        self.first.execute(env, steps)
        self.second.execute(env, steps)

    def __str__(self):
        return f"{self.first}; {self.second}"


@dataclass(frozen=True)
class If(Cmd):
    cond: Cond
    then: Cmd
    otherwise: Cmd

    def execute(self, env, steps):
        branch = self.then if self.cond.evaluate(env) else self.otherwise
        branch.execute(env, steps)

    def __str__(self):
        return f"if {self.cond} then {self.then} else {self.otherwise}"


@dataclass(frozen=True)
class While(Cmd):
    cond: Cond
    invariant: Cond
    body: Cmd
    max_iterations: int = 1000

    def execute(self, env, steps):
        iterations = 0
        while self.cond.evaluate(env):
            self.body.execute(env, steps)
            iterations += 1
            if iterations > self.max_iterations:
                raise RuntimeError("loop iteration limit exceeded")
        steps.append(dict(env))

    def __str__(self):
        return f"while {self.cond} [inv {self.invariant}] do {self.body}"


# ------------------------------------------------------------- weakest precond


def wp(cmd: Cmd, post: Cond, conditions: Optional[List[Tuple[str, Cond, Cond]]] = None) -> Cond:
    """Weakest precondition of ``cmd`` with respect to ``post``.

    While loops must carry an invariant; the function then returns the
    invariant and appends ``(name, premise, conclusion)`` implication checks to
    ``conditions``.
    """
    if conditions is None:
        conditions = []
    if isinstance(cmd, Assign):
        return post.substitute(cmd.name, cmd.expr)
    if isinstance(cmd, Seq):
        return wp(cmd.first, wp(cmd.second, post, conditions), conditions)
    if isinstance(cmd, If):
        left = AndC(cmd.cond, wp(cmd.then, post, conditions))
        right = AndC(NotC(cmd.cond), wp(cmd.otherwise, post, conditions))
        return OrC(left, right)
    if isinstance(cmd, While):
        conditions.append(
            ("preservation", AndC(cmd.invariant, cmd.cond), wp(cmd.body, cmd.invariant, conditions))
        )
        conditions.append(("exit", AndC(cmd.invariant, NotC(cmd.cond)), post))
        return cmd.invariant
    raise TypeError(f"unsupported command: {type(cmd).__name__}")


@dataclass(frozen=True)
class ImplicationCheck:
    name: str
    held: bool
    counterexample: Optional[Dict[str, int]]


def check_implication(
    premise: Cond,
    conclusion: Cond,
    bounds: Dict[str, Iterable[int]],
) -> ImplicationCheck:
    """Test ``premise => conclusion`` over a finite sample of states."""
    names = sorted(premise.variables() | conclusion.variables())
    domains = [list(bounds.get(n, range(0, 11))) for n in names]
    for values in product(*domains):
        env = dict(zip(names, values))
        if premise.evaluate(env) and not conclusion.evaluate(env):
            return ImplicationCheck("implication", False, env)
    return ImplicationCheck("implication", True, None)


@dataclass
class VerificationReport:
    pre: Cond
    post: Cond
    computed_precondition: Cond
    checks: List[ImplicationCheck]
    bounds: Dict[str, Iterable[int]]

    @property
    def all_checks_held(self) -> bool:
        return all(c.held for c in self.checks)

    def format(self) -> str:
        lines = [
            f"precondition:  {self.pre}",
            f"program is checked against postcondition: {self.post}",
            f"weakest precondition (symbolic): {self.computed_precondition}",
        ]
        for check in self.checks:
            verdict = "held" if check.held else "failed"
            lines.append(f"  - {check.name}: {verdict}")
            if check.counterexample:
                lines.append(f"    counterexample: {check.counterexample}")
        domain = ", ".join(f"{name}: {min(vals)}..{max(vals)}" for name, vals in self.bounds.items())
        lines.append(
            f"Note: checks were evaluated on the finite domain {{{domain}}} — this is "
            "evidence, not a proof for unbounded integers."
        )
        return "\n".join(lines)


def verify(
    program: Cmd,
    pre: Cond,
    post: Cond,
    bounds: Optional[Dict[str, Iterable[int]]] = None,
) -> VerificationReport:
    """Compute weakest preconditions and check the resulting implications."""
    conditions: List[Tuple[str, Cond, Cond]] = []
    computed = wp(program, post, conditions)
    bounds = bounds or {}
    names = computed.variables() | post.variables() | pre.variables()
    bounds = dict(bounds)
    for name in names:
        bounds.setdefault(name, range(0, 11))

    checks = []
    for name, premise, conclusion in conditions:
        result = check_implication(premise, conclusion, bounds)
        checks.append(ImplicationCheck(name, result.held, result.counterexample))
    initiation = check_implication(pre, computed, bounds)
    initiation = ImplicationCheck("initiation", initiation.held, initiation.counterexample)
    checks.insert(0, initiation)
    return VerificationReport(pre, post, computed, checks, bounds)


def run(program: Cmd, initial: Dict[str, int]) -> Dict[str, int]:
    """Concrete interpreter used by examples and tests."""
    env = dict(initial)
    steps: List[Dict[str, int]] = []
    steps.append(dict(env))
    program.execute(env, steps)
    return env
