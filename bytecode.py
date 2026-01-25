"""
DEPRECATED: This file has been moved to src/compiler/bytecode.py

This wrapper is provided for backward compatibility.
Please update your imports to use src.compiler.bytecode instead.
"""

import warnings

warnings.warn(
    "bytecode.py is deprecated. Use 'from src.compiler.bytecode import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

import src.compiler.bytecode as _bytecode

# Re-export public names from src.compiler.bytecode for backward compatibility
if hasattr(_bytecode, "__all__"):
    __all__ = list(_bytecode.__all__)
else:
    __all__ = [name for name in dir(_bytecode) if not name.startswith("_")]

globals().update({name: getattr(_bytecode, name) for name in __all__})

if __name__ == "__main__":
    import sys
    from src.compiler.bytecode import compile_file

    if len(sys.argv) < 2:
        print("Usage: python bytecode.py <source.syn> [output.sbc]")
        sys.exit(1)
    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    compile_file(src, out)
