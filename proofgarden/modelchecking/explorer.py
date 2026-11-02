"""Breadth-first educational model checker.

Outcome semantics (also documented in docs/limitations.md):

* ``verified``  - the whole reachable state space of the *given finite model*
  was explored and the property held there.
* ``violated``  - a reachable state falsifying the property was found; the
  result carries a counterexample trace.
* ``incomplete`` - exploration stopped at a configured limit, so no claim is
  made either way.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..state import State, StateSystem
from ..traces import Trace

Outcome = str  # "verified" | "violated" | "incomplete"

Predicate = Callable[[State], bool]


@dataclass
class ExploreResult:
    states: List[State]
    edges: List[Tuple[State, str, State]]
    deadlocks: List[State]
    complete: bool
    stop_reason: Optional[str]
    parents: Dict[State, Tuple[Optional[State], Optional[str]]] = field(default_factory=dict)


@dataclass
class CheckResult:
    property: str
    outcome: Outcome
    explored_states: int
    message: str
    trace: Optional[Trace] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "property": self.property,
            "outcome": self.outcome,
            "explored_states": self.explored_states,
            "message": self.message,
            "trace": self.trace.to_dict() if self.trace else None,
        }


class Explorer:
    """Bounded breadth-first exploration of a :class:`StateSystem`."""

    def __init__(
        self,
        system: StateSystem,
        max_states: int = 10_000,
        max_depth: Optional[int] = None,
    ) -> None:
        if max_states < 1:
            raise ValueError("max_states must be positive")
        if max_depth is not None and max_depth < 0:
            raise ValueError("max_depth must be non-negative")
        self.system = system
        self.max_states = max_states
        self.max_depth = max_depth
        self._result: Optional[ExploreResult] = None

    def explore(self) -> ExploreResult:
        if self._result is not None:
            return self._result

        parents: Dict[State, Tuple[Optional[State], Optional[str]]] = {}
        depth: Dict[State, int] = {}
        queue: deque = deque()
        order: List[State] = []
        edges: List[Tuple[State, str, State]] = []

        for state in self.system.initial_states:
            if state not in parents:
                parents[state] = (None, None)
                depth[state] = 0
                queue.append(state)

        complete = True
        stop_reason: Optional[str] = None

        while queue:
            state = queue.popleft()
            order.append(state)

            if self.max_depth is not None and depth[state] >= self.max_depth:
                continue

            successors = self.system.successors(state)
            for transition, target in successors:
                edges.append((state, transition.name, target))
                if target not in parents:
                    if len(parents) >= self.max_states:
                        complete = False
                        stop_reason = f"state limit of {self.max_states} reached"
                        break
                    if len(parents) >= 10_000_000:  # defensive, unreachable in practice
                        complete = False
                        stop_reason = "exploration aborted"
                        break
                    parents[target] = (state, transition.name)
                    depth[target] = depth[state] + 1
                    queue.append(target)
            if not complete:
                break

        if complete and self.max_depth is not None:
            # Some successors may live beyond the depth bound.
            for state in order:
                if depth[state] >= self.max_depth:
                    if self.system.successors(state):
                        complete = False
                        stop_reason = f"depth limit of {self.max_depth} reached"
                        break

        deadlocks = [s for s in order if not self.system.successors(s)]

        self._result = ExploreResult(
            states=order,
            edges=edges,
            deadlocks=deadlocks,
            complete=complete,
            stop_reason=stop_reason,
            parents=parents,
        )
        return self._result

    def check_invariant(self, name: str, violated_by: Predicate) -> CheckResult:
        """Check that ``violated_by`` is False in every reachable state."""
        result = self.explore()
        for state in result.states:
            if violated_by(state):
                trace = Trace().extend_from_parents(result.parents, state)
                return CheckResult(
                    property=f"invariant: {name}",
                    outcome="violated",
                    explored_states=len(result.states),
                    message=(
                        f"Invariant '{name}' is violated in a reachable state. "
                        "The trace shows one path to the violation."
                    ),
                    trace=trace,
                )
        if result.complete:
            return CheckResult(
                property=f"invariant: {name}",
                outcome="verified",
                explored_states=len(result.states),
                message=(
                    f"Invariant '{name}' holds in all {len(result.states)} reachable "
                    "states of the given finite model."
                ),
            )
        return CheckResult(
            property=f"invariant: {name}",
            outcome="incomplete",
            explored_states=len(result.states),
            message=(
                f"Exploration stopped early ({result.stop_reason}); no claim is made "
                f"about '{name}'."
            ),
        )

    def check_reachability(self, name: str, reached: Predicate) -> CheckResult:
        result = self.explore()
        for state in result.states:
            if reached(state):
                trace = Trace().extend_from_parents(result.parents, state)
                return CheckResult(
                    property=f"reachability: {name}",
                    outcome="verified",
                    explored_states=len(result.states),
                    message=f"Target state '{name}' is reachable; the trace shows a path.",
                    trace=trace,
                )
        if result.complete:
            return CheckResult(
                property=f"reachability: {name}",
                outcome="violated",
                explored_states=len(result.states),
                message=(
                    f"Target '{name}' is unreachable in the given finite model: all "
                    f"{len(result.states)} reachable states were explored."
                ),
            )
        return CheckResult(
            property=f"reachability: {name}",
            outcome="incomplete",
            explored_states=len(result.states),
            message=f"Exploration stopped early ({result.stop_reason}); target not found yet.",
        )

    def check_deadlock_free(self) -> CheckResult:
        result = self.explore()
        if result.deadlocks:
            state = result.deadlocks[0]
            trace = Trace().extend_from_parents(result.parents, state)
            return CheckResult(
                property="deadlock freedom",
                outcome="violated",
                explored_states=len(result.states),
                message=(
                    f"{len(result.deadlocks)} reachable state(s) have no outgoing "
                    "transition. The trace leads to the first one."
                ),
                trace=trace,
            )
        if result.complete:
            return CheckResult(
                property="deadlock freedom",
                outcome="verified",
                explored_states=len(result.states),
                message=(
                    f"No deadlocks in {len(result.states)} reachable states of the "
                    "given finite model."
                ),
            )
        return CheckResult(
            property="deadlock freedom",
            outcome="incomplete",
            explored_states=len(result.states),
            message=f"Exploration stopped early ({result.stop_reason}).",
        )
