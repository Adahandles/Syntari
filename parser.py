"""
Syntari Parser - Backwards compatibility wrapper
Import from src.interpreter.parser for actual implementation
"""

from src.interpreter.parser import (
    Parser,
    ParseError,
    parse
)

__all__ = ['Parser', 'ParseError', 'parse']

