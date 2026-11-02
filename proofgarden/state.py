"""State-transition systems.

A state is an immutable tuple of ``(variable, value)`` pairs sorted by name, so
states are hashable and comparable without custom machinery.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

State = Tuple[Tuple[str, Any], ...]

Guard = Callable[[State], bool]
Action = Callable[[State], State]


def make_state(values: Mapping[str, Any]) -> State:
    return tuple(sorted(values.items()))


def state_dict(state: State) -> Dict[str, Any]:
    return dict(state)


@dataclass(frozen=True)
class Transition:
    name: str
    guard: Guard
    action: Action


@dataclass
class StateSystem:
    """A finite or finitely-generable transition system."""

    name: str
    initial_states: Tuple[State, ...]
    transitions: Tuple[Transition, ...]
    variables: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.initial_states:
            raise ValueError("a state system needs at least one initial state")
        if not self.transitions:
            raise ValueError("a state system needs at least one transition")
        names = [t.name for t in self.transitions]
        if len(set(names)) != len(names):
            raise ValueError("transition names must be unique")

    def successors(self, state: State) -> List[Tuple[Transition, State]]:
        result: List[Tuple[Transition, State]] = []
        for transition in self.transitions:
            if transition.guard(state):
                target = transition.action(state)
                result.append((transition, target))
        return result


def system_from_python(
    name: str,
    initial: Sequence[Mapping[str, Any]],
    transitions: Sequence[Tuple[str, Guard, Action]],
) -> StateSystem:
    return StateSystem(
        name=name,
        initial_states=tuple(make_state(s) for s in initial),
        transitions=tuple(Transition(n, g, a) for n, g, a in transitions),
    )


@dataclass(frozen=True)
class JsonInvariant:
    """An invariant expressed as forbidden state patterns.

    A pattern matches a state when every ``key: value`` pair in the pattern is
    present in the state with the same value. Matching states violate the
    invariant; this subset semantics is deliberately simple and auditable.
    """

    name: str
    description: str
    forbidden: Tuple[Tuple[str, Any], ...]

    def violated_by(self, state: State) -> bool:
        values = dict(state)
        return all(values.get(k) == v for k, v in self.forbidden)


def load_system(path: str | Path) -> Tuple[StateSystem, List[JsonInvariant], Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Load a model from JSON.

    Returns ``(system, invariants, reachability_target, deadlock_expectation)``.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for required in ("name", "initial", "edges"):
        if required not in data:
            raise ValueError(f"model file missing required key: {required}")

    states: Dict[State, None] = {}
    lookup: Dict[State, Dict[str, Any]] = {}

    def register(values: Mapping[str, Any]) -> State:
        state = make_state(values)
        states[state] = None
        lookup[state] = dict(values)
        return state

    initial_states = [register(s) for s in data["initial"]]
    edge_table: Dict[State, List[Tuple[str, State]]] = {}

    for edge in data["edges"]:
        if not {"from", "to"} <= set(edge):
            raise ValueError("each edge needs 'from' and 'to'")
        src = register(edge["from"])
        dst = register(edge["to"])
        label = edge.get("label", "step")
        edge_table.setdefault(src, []).append((label, dst))

    # Build transitions that implement the explicit edge relation. One
    # transition per label keeps names unique; its guard/action consult the
    # edge table, so exploration still uses the normal StateSystem interface.
    labels: List[str] = []
    for edges in edge_table.values():
        for label, _ in edges:
            if label not in labels:
                labels.append(label)

    transitions = []
    for label in labels:
        def guard(state: State, _label: str = label) -> bool:
            return any(lbl == _label for lbl, _ in edge_table.get(state, []))

        def action(state: State, _label: str = label) -> State:
            for lbl, dst in edge_table.get(state, []):
                if lbl == _label:
                    return dst
            raise ValueError(f"transition {_label!r} has no target from {state}")

        transitions.append((label, guard, action))

    system = system_from_python(
        name=data["name"],
        initial=[lookup[s] for s in initial_states],
        transitions=transitions,
    )

    invariants = [
        JsonInvariant(
            name=inv["name"],
            description=inv.get("description", ""),
            forbidden=make_state(inv["forbidden"]),
        )
        for inv in data.get("invariants", [])
    ]

    target = data.get("reachability_target")
    deadlock = data.get("expect_deadlock")
    return system, invariants, target, deadlock
