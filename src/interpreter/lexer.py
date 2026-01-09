"""
Simple lexer implementation for the interpreter.

This module provides a minimal `lex` function that turns a source string
into a sequence of tokens. It is intentionally small and generic so it can
be reused by the rest of the interpreter without imposing a specific
language design.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class Token:
    """Represents a single lexical token."""

    type: str
    value: str
    line: int
    column: int


# Token specification: ordered list of named regex groups.
_TOKEN_SPECIFICATION = [
    ("NUMBER", r"\d+(\.\d+)?"),
    ("IDENT", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("OP", r"==|!=|<=|>=|[+\-*/%=<>]"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("COMMA", r","),
    ("SEMICOLON", r";"),
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

_TOK_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in _TOKEN_SPECIFICATION)
)


def lex(source: str) -> List[Token]:
    """
    Lexically analyze the given source string into tokens.

    Whitespace is skipped, newlines are returned as `NEWLINE` tokens,
    and any unexpected character results in a SyntaxError.
    """
    tokens: List[Token] = []
    line = 1
    line_start = 0

    for match in _TOK_REGEX.finditer(source):
        kind = match.lastgroup
        value = match.group()
        column = match.start() - line_start + 1

        if kind == "NUMBER":
            tokens.append(Token("NUMBER", value, line, column))
        elif kind == "IDENT":
            tokens.append(Token("IDENT", value, line, column))
        elif kind == "OP":
            tokens.append(Token("OP", value, line, column))
        elif kind == "LPAREN":
            tokens.append(Token("LPAREN", value, line, column))
        elif kind == "RPAREN":
            tokens.append(Token("RPAREN", value, line, column))
        elif kind == "LBRACE":
            tokens.append(Token("LBRACE", value, line, column))
        elif kind == "RBRACE":
            tokens.append(Token("RBRACE", value, line, column))
        elif kind == "COMMA":
            tokens.append(Token("COMMA", value, line, column))
        elif kind == "SEMICOLON":
            tokens.append(Token("SEMICOLON", value, line, column))
        elif kind == "NEWLINE":
            tokens.append(Token("NEWLINE", value, line, column))
            line += 1
            line_start = match.end()
        elif kind == "SKIP":
            pass
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character {value!r} at line {line}, column {column}")

    return tokens


def tokenize(source: str) -> List[Token]:
    """
    Alias for lex() to maintain compatibility with existing code.
    
    Args:
        source: The input string to tokenize.
    
    Returns:
        A list of Token instances.
    """
    return lex(source)
