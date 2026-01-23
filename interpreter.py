"""
Syntari Interpreter - Backwards compatibility wrapper
Import from src.interpreter.interpreter for actual implementation
"""

from src.interpreter.interpreter import (
    Interpreter,
    RuntimeError,
    ReturnValue,
    Environment,
    interpret
)

__all__ = ['Interpreter', 'RuntimeError', 'ReturnValue', 'Environment', 'interpret']

