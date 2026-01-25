"""
DEPRECATED: This file has been moved to src/vm/runtime.py

This wrapper is provided for backward compatibility.
Please update your imports to use src.vm.runtime instead.
"""

import warnings

warnings.warn(
    "runtime.py is deprecated. Use 'from src.vm.runtime import ...' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.vm.runtime import *

if __name__ == "__main__":
    import sys
    from src.vm.runtime import run_vm

    if len(sys.argv) < 2:
        print("Usage: python runtime.py <file.sbc>")
        sys.exit(1)
    run_vm(sys.argv[1])
