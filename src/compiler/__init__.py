"""
Syntari Compiler Module - Bytecode compilation and code generation.

This package exposes the canonical bytecode backend for Syntari v0.3 via ``bytecode.py``.
The alternative implementation in ``bytecode_v2.py`` is currently experimental / reserved
for future work and is intentionally not exported from this module's public API.
"""

# Public compiler interface for the stable v0.3 bytecode backend.
from .bytecode import BytecodeGenerator, compile_file, OPCODES

__all__ = ["BytecodeGenerator", "compile_file", "OPCODES"]
