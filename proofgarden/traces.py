"""Structured counterexample traces."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .state import State


@dataclass(frozen=True)
class TraceStep:
    index: int
    state: Dict[str, Any]
    transition: Optional[str]  # transition label that produced this state

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "state": self.state,
            "transition": self.transition,
        }


@dataclass
class Trace:
    steps: List[TraceStep] = field(default_factory=list)

    def append(self, state: State, transition: Optional[str]) -> None:
        self.steps.append(TraceStep(len(self.steps), dict(state), transition))

    def extend_from_parents(self, parents: Dict[State, Tuple[Optional[State], Optional[str]]], state: State) -> "Trace":
        """Rebuild the path to ``state`` using a parent map."""
        chain: List[Tuple[State, Optional[str]]] = []
        cursor: Optional[State] = state
        while cursor is not None:
            parent, label = parents[cursor]
            chain.append((cursor, label))
            cursor = parent
        chain.reverse()
        self.steps = [TraceStep(i, dict(s), label) for i, (s, label) in enumerate(chain)]
        return self

    def format(self) -> str:
        lines = []
        for step in self.steps:
            label = step.transition or "(initial)"
            lines.append(f"  {step.index}. {dict(step.state)}  <- {label}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {"steps": [s.to_dict() for s in self.steps]}
