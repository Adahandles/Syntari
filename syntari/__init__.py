"""
Syntari - AI-integrated, type-safe, functional-first programming language.

This package exposes the public Python API for embedding Syntari in other
applications (e.g. Chain-Of-Record).  Import ``syntari.api`` for the
high-level ``validate`` / ``execute`` entry points.
"""

try:
    from src.__version__ import __version__  # re-export canonical version
except ImportError:  # pragma: no cover
    __version__ = "0.4.0"

__all__ = ["__version__"]
