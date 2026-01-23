"""
Syntari Lexer - Backwards compatibility wrapper
Import from src.interpreter.lexer for actual implementation
"""

from src.interpreter.lexer import (
    TokenType,
    Token,
    Lexer,
    LexerError,
    tokenize
)

__all__ = ['TokenType', 'Token', 'Lexer', 'LexerError', 'tokenize']

