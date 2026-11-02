"""Propositional logic: parser, evaluator, truth tables, SAT."""

from .parser import ParseError, parse

__all__ = ["parse", "ParseError"]
