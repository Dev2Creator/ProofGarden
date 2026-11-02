"""Recursive-descent parser for propositional formulas.

Grammar (lowest precedence first):

    iff      := implies (IFF implies)*
    implies  := or (IMPLIES implies)?          # right associative
    or       := xor (OR xor)*
    xor      := and (XOR and)*
    and      := unary (AND unary)*
    unary    := NOT unary | atom
    atom     := NAME | TRUE | FALSE | "(" iff ")"
"""

from __future__ import annotations

from typing import List

from .ast import BinOp, Const, Expr, Not, Var
from .lexer import Token, tokenize


class ParseError(ValueError):
    """Raised for syntactically invalid formulas."""

    def __init__(self, message: str, token: Token) -> None:
        where = f"at character {token.position + 1}"
        found = token.text if token.kind != "EOF" else "end of input"
        super().__init__(f"{message} {where} (found {found!r})")
        self.token = token


class _Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    @property
    def current(self) -> Token:
        return self.tokens[self.index]

    def advance(self) -> Token:
        tok = self.current
        self.index += 1
        return tok

    def expect(self, kind: str, message: str) -> Token:
        if self.current.kind != kind:
            raise ParseError(message, self.current)
        return self.advance()

    def parse(self) -> Expr:
        expr = self.parse_iff()
        if self.current.kind != "EOF":
            raise ParseError("unexpected trailing input", self.current)
        return expr

    def parse_iff(self) -> Expr:
        expr = self.parse_implies()
        while self.current.kind == "IFF":
            self.advance()
            expr = BinOp("IFF", expr, self.parse_implies())
        return expr

    def parse_implies(self) -> Expr:
        left = self.parse_or()
        if self.current.kind == "IMPLIES":
            self.advance()
            return BinOp("IMPLIES", left, self.parse_implies())
        return left

    def parse_or(self) -> Expr:
        expr = self.parse_xor()
        while self.current.kind == "OR":
            self.advance()
            expr = BinOp("OR", expr, self.parse_xor())
        return expr

    def parse_xor(self) -> Expr:
        expr = self.parse_and()
        while self.current.kind == "XOR":
            self.advance()
            expr = BinOp("XOR", expr, self.parse_and())
        return expr

    def parse_and(self) -> Expr:
        expr = self.parse_unary()
        while self.current.kind == "AND":
            self.advance()
            expr = BinOp("AND", expr, self.parse_unary())
        return expr

    def parse_unary(self) -> Expr:
        if self.current.kind == "NOT":
            self.advance()
            return Not(self.parse_unary())
        return self.parse_atom()

    def parse_atom(self) -> Expr:
        tok = self.current
        if tok.kind == "NAME":
            self.advance()
            return Var(tok.text)
        if tok.kind == "CONST":
            self.advance()
            return Const(tok.text.upper() == "TRUE")
        if tok.kind == "LPAREN":
            self.advance()
            expr = self.parse_iff()
            self.expect("RPAREN", "expected ')' to close the group")
            return expr
        raise ParseError("expected a variable, constant or '('", tok)


def parse(source: str) -> Expr:
    """Parse ``source`` into a formula or raise :class:`ParseError`."""
    if not source or not source.strip():
        raise ParseError("empty formula", Token("EOF", "", 0))
    return _Parser(tokenize(source)).parse()
