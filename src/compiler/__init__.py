"""
Syntari Compiler Module

Enhanced bytecode compilation with optimizations.
"""

from .bytecode_v2 import (
    BytecodeCompilerV2,
    Opcode,
    compile_file,
    CompileError,
    OptimizationPass,
    ConstantFoldingPass,
    DeadCodeEliminationPass,
)

__all__ = [
    "BytecodeCompilerV2",
    "Opcode",
    "compile_file",
    "CompileError",
    "OptimizationPass",
    "ConstantFoldingPass",
    "DeadCodeEliminationPass",
]
