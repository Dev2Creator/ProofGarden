"""Tokenizer for the propositional-logic surface syntax."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List


class LexError(ValueError):
    """Raised when input contains a character the grammar cannot accept."""

    def __init__(self, message: str, position: int) -> None:
        super().__init__(f"{message} (at character {position + 1})")
        self.position = position


@dataclass(frozen=True)
class Token:
    kind: str  # NAME, CONST, NOT, AND, OR, XOR, IMPLIES, IFF, LPAREN, RPAREN
    text: str
    position: int


_KEYWORDS = {
    "NOT": "NOT",
    "AND": "AND",
    "OR": "OR",
    "XOR": "XOR",
    "IMPLIES": "IMPLIES",
    "IFF": "IFF",
    "TRUE": "CONST",
    "FALSE": "CONST",
}

# Symbolic spellings mapped onto the same token kinds.
_SYMBOLS = {
    "~": "NOT",
    "!": "NOT",
    "¬": "NOT",
    "&": "AND",
    "&&": "AND",
    "∧": "AND",
    "|": "OR",
    "||": "OR",
    "∨": "OR",
    "^": "XOR",
    "⊕": "XOR",
    "->": "IMPLIES",
    "=>": "IMPLIES",
    "→": "IMPLIES",
    "<->": "IFF",
    "<=>": "IFF",
    "↔": "IFF",
}

_MULTI_CHAR = ("<->", "<=>", "->", "=>", "&&", "||")


def tokenize(source: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(source)
    while i < n:
        ch = source[i]
        if ch.isspace():
            i += 1
            continue
        if ch == "(":
            tokens.append(Token("LPAREN", ch, i))
            i += 1
            continue
        if ch == ")":
            tokens.append(Token("RPAREN", ch, i))
            i += 1
            continue
        matched = None
        for sym in _MULTI_CHAR:
            if source.startswith(sym, i):
                matched = sym
                break
        if matched is not None:
            tokens.append(Token(_SYMBOLS[matched], matched, i))
            i += len(matched)
            continue
        if ch in _SYMBOLS:
            tokens.append(Token(_SYMBOLS[ch], ch, i))
            i += 1
            continue
        if ch.isalpha() or ch == "_":
            start = i
            while i < n and (source[i].isalnum() or source[i] == "_"):
                i += 1
            word = source[start:i]
            upper = word.upper()
            kind = _KEYWORDS.get(upper, "NAME")
            tokens.append(Token(kind, word, start))
            continue
        raise LexError(f"unexpected character {ch!r}", i)
    tokens.append(Token("EOF", "", n))
    return tokens
